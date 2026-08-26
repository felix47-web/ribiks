MALE_NAMES = set()
FEMALE_NAMES = set()


def _load_names():
    global MALE_NAMES, FEMALE_NAMES
    if MALE_NAMES or FEMALE_NAMES:
        return

    male_nigerian = [
        "Emeka", "Obinna", "Chinedu", "Chukwuemeka", "Ikem", "Nnamdi", "Uche", "Chidi",
        "Chiagozie", "Obiora", "Ifeanyichukwu", "Chibueze", "Uchenna", "Arinze", "Kelechi",
        "Tunde", "Femi", "Wale", "Yemi", "Segun", "Deji", "Bola", "Dipo", "Kola", "Biola",
        "Kayode", "Gbenga", "Funmi", "Lanre", "Sola", "Tobi", "Damilare", "Oluwaseun",
        "Adewale", "Adeniyi", "Ayomide", "Oluwatobi", "Babatunde", "Olumide", "Olawale",
        "Musa", "Ibrahim", "Ahmad", "Abubakar", "Yusuf", "Umar", "Aliyu", "Suleiman",
        "Usman", "Hassan", "Hussain", "Abdullahi", "Ismail", "Tukur", "Lawal", "Garba",
        "Mukhtar", "Bala", "Danjuma", "Sani", "Bello", "Rabiu", "Ali", "Omar", "Ibrahim",
        "Chukwuma", "Adekunle", "Olusegun", "Akinwale", "Oluwole", "Adeyemi", "Olatunji",
        "Folake", "Adewunmi", "Oluwadamilare", "Temidayo", "Babajide", "Oluwatosin",
    ]

    female_nigerian = [
        "Chioma", "Nneka", "Adaeze", "Chiamaka", "Ngozi", "Ifeoma", "Chisom", "Obiageli",
        "Akwaugo", "Chidinma", "Ifeanyi", "Azubuike", "Ogechi", "Amaka", "Ujunwa", "Nkiruka",
        "Folake", "Funke", "Bukola", "Yetunde", "Sade", "Yewande", "Titilayo", "Morenike",
        "Olubunmi", "Aderonke", "Olayinka", "Aminat", "Aisha", "Fatima", "Zainab", "Hauwa",
        "Amina", "Halima", "Maryam", "Sa'adatu", "Rashida", "Hafsat", "Jamila", "Rabi",
        "Adeola", "Oluwabunmi", "Olubunmi", "Oluwaseyi", "Bolaji", "Kemi", "Sade", "Peju",
        "Dupe", "Folasade", "Toyin", "Ronke", "Nike", "Bola", "Moji", "Titi", "Laide",
        "Adenike", "Omotola", "Genevieve", "Stella", "Grace", "Blessing", "Patience",
        "Mercy", "Esther", "Favour", "Success", "Precious", "Vivian", "Gloria", "Joy",
        "Peace", "Hope", "Charity", "Faith", "Priscilla", "Rebecca", "Sarah", "Hannah",
        "Deborah", "Ruth", "Victoria", "Felicia", "Cynthia", "Gladys", "Beatrice",
    ]

    male_american = [
        "James", "Michael", "Robert", "John", "David", "William", "Richard", "Joseph",
        "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Mark",
        "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth", "Kevin", "Brian",
        "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan", "Jacob",
        "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott",
        "Brandon", "Benjamin", "Samuel", "Raymond", "Gregory", "Frank", "Alexander",
        "Patrick", "Jack", "Dennis", "Jerry", "Tyler", "Aaron", "Jose", "Adam",
        "Nathan", "Henry", "Douglas", "Zachary", "Peter", "Kyle", "Noah", "Ethan",
        "Jeremy", "Walter", "Christian", "Keith", "Roger", "Terry", "Austin", "Sean",
        "Gerald", "Carl", "Harold", "Dylan", "Arthur", "Lawrence", "Jordan", "Jesse",
        "Bryan", "Billy", "Bruce", "Gabriel", "Joe", "Logan", "Albert", "Willie",
        "Alan", "Eugene", "Russell", "Vincent", "Philip", "Bobby", "Harry", "Roy",
        "Elijah", "Randy", "Wayne", "Louis", "Ralph", "Roy", "Eugene", "Russell",
        "Liam", "Noah", "Oliver", "Lucas", "Mason", "Logan", "Alexander", "Ethan",
        "Jacob", "William", "Jayden", "Benjamin", "James", "Henry", "Sebastian",
        "Mateo", "Jack", "Owen", "Samuel", "Ryan", "Levi", "Nathan", "Carter",
    ]

    female_american = [
        "Mary", "Patricia", "Jennifer", "Linda", "Barbara", "Elizabeth", "Susan",
        "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
        "Ashley", "Dorothy", "Kimberly", "Emily", "Donna", "Michelle", "Carol",
        "Amanda", "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura",
        "Cynthia", "Kathleen", "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela",
        "Emma", "Nicole", "Helen", "Samantha", "Katherine", "Christine", "Debra",
        "Rachel", "Carolyn", "Janet", "Catherine", "Maria", "Heather", "Diane",
        "Ruth", "Julie", "Olivia", "Joyce", "Virginia", "Victoria", "Kelly", "Lauren",
        "Christina", "Joan", "Evelyn", "Judith", "Megan", "Andrea", "Cheryl",
        "Hannah", "Jacqueline", "Martha", "Gloria", "Teresa", "Ann", "Sara", "Madison",
        "Frances", "Kathryn", "Janice", "Jean", "Abigail", "Alice", "Judy", "Sophia",
        "Grace", "Denise", "Amber", "Doris", "Marilyn", "Danielle", "Beverly",
        "Isabella", "Priya", "Olivia", "Sophia", "Mia", "Charlotte", "Amelia",
        "Harper", "Evelyn", "Abigail", "Emily", "Ella", "Elizabeth", "Camila",
        "Luna", "Sofia", "Avery", "Mila", "Aria", "Scarlett", "Penelope", "Layla",
        "Chloe", "Victoria", "Madison", "Eleanor", "Grace", "Nora", "Riley",
        "Zoey", "Hannah", "Hazel", "Lily", "Ellie", "Stella", "Natalie", "Zoe",
        "Leah", "Harper", "Rosie", "Aubrey", "Brooklyn", "Claire", "Paisley",
    ]

    male_european = [
        "Pierre", "Jacques", "Louis", "Andre", "Marcel", "Claude", "Henri", "Philippe",
        "Jean", "Michel", "Alain", "Bernard", "Gilles", "Laurent", "Stephane", "Nicolas",
        "Sebastien", "Olivier", "Frederic", "Antoine", "Romain", "Julien", "Quentin",
        "Hugo", "Lucas", "Nathan", "Leo", "Maxime", "Alexandre", "Thomas", "Matthieu",
        "Pablo", "Carlos", "Miguel", "Jorge", "Antonio", "Manuel", "Pedro", "Luis",
        "Sergio", "Rafael", "Fernando", "Diego", "Alejandro", "Adrian", "Dani",
        "Pablo", "Xavier", "Andres", "Eduardo", "Oscar", "Ivan", "Marc", "Sergi",
        "Hans", "Klaus", "Werner", "Stefan", "Wolfgang", "Jurgen", "Heinrich", "Fritz",
        "Karl", "Friedrich", "Otto", "Ludwig", "Max", "Franz", "Peter", "Martin",
        "Andreas", "Thomas", "Michael", "Wolfgang", "Manfred", "Helmut", "Dieter",
        "Marco", "Luca", "Giovanni", "Matteo", "Alessandro", "Francesco", "Lorenzo",
        "Davide", "Gabriele", "Andrea", "Federico", "Roberto", "Giuseppe", "Paolo",
        "Piotr", "Wojciech", "Krzysztof", "Tomasz", "Marcin", "Jakub", "Adam",
        "Michal", "Jan", "Mateusz", "Mikhail", "Dmitri", "Sergei", "Andrei", "Nikolai",
        "Alexei", "Vladimir", "Igor", "Boris", "Viktor", "Oleg", "Yuri", "Alexandr",
        "Oliver", "George", "Harry", "Jack", "Oscar", "Charlie", "Thomas", "William",
        "Henry", "Alfie", "Joshua", "Ethan", "Freddie", "Archie", "James", "Logan",
    ]

    female_european = [
        "Marie", "Jeanne", "Claire", "Monique", "Francoise", "Catherine", "Sylvie",
        "Isabelle", "Nathalie", "Sophie", "Helene", "Veronique", "Sandrine", "Cecile",
        "Camille", "Juliette", "Manon", "Lea", "Chloe", "Ines", "Marine", "Pauline",
        "Margaux", "Celeste", "Adeline", "Elise", "Rosalie", "Juliette", "Emma",
        "Maria", "Carmen", "Rosa", "Ana", "Laura", "Cristina", "Isabel", "Elena",
        "Sonia", "Pilar", "Lucia", "Martina", "Paula", "Adriana", "Sara", "Daniela",
        "Laia", "Carla", "Julia", "Irene", "Aina", "Marta", "Nuria", "Clara",
        "Greta", "Hannah", "Anna", "Lena", "Sophie", "Julia", "Lea", "Lara",
        "Amelie", "Mia", "Emilia", "Clara", "Hannah", "Lina", "Ella", "Leoni",
        "Giulia", "Francesca", "Alessia", "Giorgia", "Sara", "Martina", "Chiara",
        "Valentina", "Giulia", "Eleonora", "Aurora", "Ginevra", "Vittoria", "Bianca",
        "Katarzyna", "Agnieszka", "Malgorzata", "Anna", "Magdalena", "Paulina",
        "Zuzanna", "Aleksandra", "Natalia", "Weronika", "Joanna", "Dominika",
        "Anastasia", "Olga", "Natalia", "Maria", "Ekaterina", "Anna", "Tatiana",
        "Irina", "Elena", "Svetlana", "Tatyana", "Yuliya", "Marina", "Daria",
        "Sophie", "Olivia", "Isla", "Emily", "Ella", "Poppy", "Ava", "Isabella",
        "Mia", "Freya", "Phoebe", "Evie", "Ruby", "Grace", "Ivy", "Rosie",
        "Lottie", "Jessica", "Polly", "Daisy", "Florence", "Esme", "Willow",
    ]

    MALE_NAMES = (
        set(male_nigerian) | set(male_american) | set(male_european)
    )
    FEMALE_NAMES = (
        set(female_nigerian) | set(female_american) | set(female_european)
    )


def detect_gender_from_name(name):
    _load_names()
    if not name:
        return "unknown"

    first = name.strip().split()[0].capitalize()

    if first in MALE_NAMES:
        return "male"
    if first in FEMALE_NAMES:
        return "female"

    return "unknown"


def detect_gender_with_ai(name, api_key, model="gpt-4o-mini"):
    import requests

    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Reply with ONLY one word: 'male' or 'female' based on the name's most likely gender. No explanation."
                },
                {
                    "role": "user",
                    "content": f"Name: {name}"
                }
            ],
            "max_tokens": 10,
            "temperature": 0
        }
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json=payload, headers=headers, timeout=10
        )
        if resp.status_code == 200:
            answer = resp.json()["choices"][0]["message"]["content"].strip().lower()
            if "male" in answer or "female" in answer:
                return "female" if "female" in answer else "male"
    except Exception:
        pass

    return "unknown"


def detect_gender(name, api_key=None, model="gpt-4o-mini"):
    result = detect_gender_from_name(name)
    if result != "unknown":
        return result

    if api_key:
        result = detect_gender_with_ai(name, api_key, model)
        if result != "unknown":
            return result

    return "unknown"


def get_gender_emoji(gender):
    if gender == "male":
        return "👨"
    elif gender == "female":
        return "👩"
    return "❓"
