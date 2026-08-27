import asyncio
import os
import shutil
import socket
import subprocess
import time

from .config import BASE_DIR

SOCKS_HOST = "127.0.0.1"
SOCKS_PORT = 9050

TOR_DATA_DIR = os.path.join(BASE_DIR, ".tor_data")
TOR_LOG_DIR = os.path.join(BASE_DIR, ".tor")
TOR_LOG = os.path.join(TOR_LOG_DIR, "tor.log")


def _find_geoip():
    """Locate the Tor GEOIP database.

    Tor needs this to map relays to countries so that ExitNodes ({us}/{de})
    can be enforced. Paths vary by distro, and the default config often points
    at an empty tmp dir, so we search the common locations across Termux and
    Linux distributions.
    """
    candidates = [
        "/data/data/com.termux/files/usr/share/tor/geoip",
        "/usr/share/tor/geoip",
        "/usr/local/share/tor/geoip",
        "/usr/share/geoip/GeoIP.dat",
        "/usr/share/GeoIP/GeoIP.dat",
        "/var/lib/tor/geoip",
        "/usr/lib/tor/geoip",
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            return p
    return None


def _geoip_install_hint():
    """Return a human-friendly hint for installing the Tor country database."""
    hints = []
    if shutil.which("apt"):
        hints.append("    - Debian/Ubuntu/Kali: sudo apt install tor-geoipdb")
    if shutil.which("pkg"):
        hints.append("    - Termux: the geoip ships with the tor package already")
    return "\n".join(hints)

# Maps ribiks location codes -> Tor ExitNodes country codes.
# "us" -> United States, "de" -> Germany.
EXIT_NODES = {
    "us": "{us}",
    "de": "{de}",
}

# In-memory flag recording whether *this* process started Tor.
# We only auto-stop Tor that we launched, never one already running.
_started_here = False


def is_tor_installed():
    return shutil.which("tor") is not None


def tor_running():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((SOCKS_HOST, SOCKS_PORT))
        sock.close()
        return result == 0
    except Exception:
        return False


# Telegram MTProto reach a public, stable set of DC IPs. Probing one of these
# over the SOCKS proxy confirms the circuit can actually carry the traffic
# ribiks relies on, without triggering Tor's DNS-leak warning (we connect by IP).
TG_DC_HOSTS = [
    "149.154.167.50",  # DC2
    "149.154.175.50",  # DC3
    "91.108.56.130",   # DC4
    "91.108.56.170",   # DC5
]
TG_PROBE_PORT = 443


def _proxy_usable():
    """Attempt a real SOCKS5 TCP connect through the local Tor.

    The SOCKS listener opens almost immediately, but Tor must finish
    bootstrapping (build its first exit circuit) before it can carry traffic.
    We probe a Telegram DC IP over the proxy to confirm the circuit is usable
    for the actual MTProto path ribiks needs.
    """
    try:
        from python_socks.async_.asyncio import Proxy

        proxy_holder = {}

        async def _build_proxy():
            # python_socks 3.x needs a running event loop at construction time.
            proxy_holder["proxy"] = Proxy.from_url(
                f"socks5://{SOCKS_HOST}:{SOCKS_PORT}"
            )

        async def _probe_loop():
            await _build_proxy()
            proxy = proxy_holder["proxy"]
            for host in TG_DC_HOSTS:
                try:
                    sock = await asyncio.wait_for(
                        proxy.connect(host, TG_PROBE_PORT), timeout=15
                    )
                    # python_socks 3.x returns a socket-like object; older
                    # versions returned a (reader, writer) pair.
                    if isinstance(sock, tuple):
                        sock[1].close()
                    elif hasattr(sock, "close"):
                        sock.close()
                    return True
                except Exception:
                    continue
            return False

        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_probe_loop()) is True
        finally:
            loop.close()
    except Exception:
        return False


def _normalize_location(exit_location):
    """Return a Tor ExitNodes value for a ribiks location code.

    Unknown/invalid values fall back to US so the connection is still
    forced through a single chosen country rather than degrading to real IP.
    """
    loc = (exit_location or "").lower().strip()
    return EXIT_NODES.get(loc, EXIT_NODES["us"])


def ensure_tor(exit_location="us"):
    """Start the Tor daemon (if not already running) and wait for it to listen.

    The connection is forced through the exit country matching `exit_location`
    (us | de) using ExitNodes + StrictNodes, so Telegram sees an IP from that
    country rather than the device's real location.
    """
    global _started_here

    if not is_tor_installed():
        print("[!] Tor is not installed. Ribiks anonymizes Telegram via Tor.")
        print("[i] Install it, then run 'ribiks setup' again:")
        print("    - Termux : pkg install tor")
        print("    - Debian / Ubuntu / Kali : sudo apt install tor")
        return False

    if tor_running():
        if not _started_here:
            # A Tor already runs (maybe started by the user or another tool).
            # We can't know its exit policy, so warn but proceed in case it is
            # already configured as desired.
            print("[+] Anonymity: Tor already running on 127.0.0.1:9050")
        return True

    os.makedirs(TOR_DATA_DIR, exist_ok=True)
    os.makedirs(TOR_LOG_DIR, exist_ok=True)

    exit_nodes = _normalize_location(exit_location)

    cmd = [
        "tor",
        "--DataDirectory", TOR_DATA_DIR,
        "--SOCKSPort", f"{SOCKS_HOST}:{SOCKS_PORT}",
        "--ExitNodes", exit_nodes,
        "--StrictNodes", "1",
        "--RunAsDaemon", "1",
        "--Log", f"notice file {TOR_LOG}",
    ]

    # GEOIP makes country-based ExitNodes enforceable. Without it Tor cannot
    # tell which country a relay belongs to and the US/DE restriction fails.
    # (GeoIPFile is the supported option; it covers the IPv4 country table
    # that matters for restricting exits.)
    geoip4 = _find_geoip()
    if geoip4:
        cmd += ["--GeoIPFile", geoip4]
    else:
        print("[w] GEOIP database not found — the chosen country exit may not be enforced.")
        hint = _geoip_install_hint()
        if hint:
            print(f"[i] To enforce the {exit_location.upper()} exit, install the Tor country database:")
            print(hint)
        else:
            print("[i] Add '--GeoIPFile <path-to-geoip>' so Tor knows which relays are in which country.")

    print(f"[*] Starting Tor (exit: {exit_location.upper()})...")
    try:
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except Exception as e:
        print(f"[!] Failed to start Tor: {e}")
        return False

    # Wait for the SOCKS listener to come up AND for Tor to finish bootstrap
    # (build a usable exit circuit). The port opens fast, but traffic can only
    # flow once a circuit exists, so we poll for a real connection attempt.
    deadline = time.time() + 60
    printed_ready = False
    while time.time() < deadline:
        if tor_running() and not _started_here:
            _started_here = True
        if _started_here and _proxy_usable():
            print(f"[+] Anonymity: active — Telegram routed through Tor (exit: {exit_location.upper()})")
            return True
        if tor_running() and not printed_ready:
            print("[*] Tor up, building circuit...")
            printed_ready = True
        time.sleep(2)

    print("[!] Tor circuit did not become usable in time.")
    print(f"    Check log: {TOR_LOG}")
    return False


def get_socks_proxy():
    """Return the proxy object Telethon needs to connect through the local Tor.

    python_socks must be installed for Telethon to honor a SOCKS proxy; without
    it Telethon silently ignores the proxy and would connect directly, leaking
    the device's real location. So if it is missing we fail clearly instead of
    silently connecting unprotected.
    """
    try:
        from python_socks import ProxyType

        return (ProxyType.SOCKS5, SOCKS_HOST, SOCKS_PORT, True)
    except ImportError:
        print("[!] 'python-socks' is not installed, so the Tor proxy cannot "
              "be used and ribiks would leak your real location.")
        print("[i] Install it and try again:")
        print("    - pip install python-socks")
        return None


def stop_tor():
    """Shut down Tor only if this process started it."""
    global _started_here

    if not _started_here:
        return

    print("[i] Anonymity: stopping Tor...")
    # Match only the Tor we launched (identified by our DataDirectory), so we
    # never kill a different Tor instance the user or another tool runs.
    marker = f"--DataDirectory {TOR_DATA_DIR}"
    pid = None
    try:
        out = subprocess.run(
            ["pgrep", "-f", f"tor {marker}"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        for line in out.stdout.splitlines():
            line = line.strip()
            if line.isdigit():
                pid = line
                break
    except Exception:
        pid = None

    if pid:
        try:
            subprocess.run(["kill", "-TERM", pid], capture_output=True, text=True, timeout=10)
        except Exception:
            pass

    # Fallback: broad match on our exact DataDirectory path.
    try:
        subprocess.run(
            ["pkill", "-f", marker],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        pass

    _started_here = False

