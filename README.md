# Flashcard-Web-App

Flashcard-Web-App este o aplicție web dezvoltată cu **Django**, care permite utilizatorilor să creeze, să editeze și să testeze cunoștințele folosind **flashcards**. Aplicația include atât **seturi definite de utilizator**, cât și **seturi predefinite**, cu sistem de **quiz** și **monitorizare progres**.

---

## Tehnologii folosite

### Backend
- Python 3.10+
- Django 5.2.8
- SQLite (implicit)

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- Django Templates

### Concepte utilizate
- MVC (Model-View-Template)
- Strategy Pattern
- DTO (Data Transfer Object)
- Django Sessions
- JSON pentru date predefinite

---

## Structura proiectului

```text
Flashcard-Web-App/
│
├── .venv/                       # virtual environment
│
├── myproject/
│   ├── flashcards/
│   │   ├── data/
│   │   │   └── predefined_sets.json
│   │   │
│   │   ├── migrations/
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_flashcardprogress.py
│   │   │   ├── 0003_alter_flashcardset_name.py
│   │   │   └── 0004_flashcardprogress_predefined_key.py
│   │   │
│   │   ├── services/
│   │   │   └── predefined_loader.py
│   │   │
│   │   ├── strategies/
│   │   │   ├── answer_strategy.py
│   │   │   ├── exact_match.py
│   │   │   └── quiz_evaluator.py
│   │   │
│   │   ├── templates/
│   │   │   ├── progress/
│   │   │   │   └── my_progress.html
│   │   │   ├── quiz/
│   │   │   │   ├── predefined_take_quiz.html
│   │   │   │   ├── quiz_finished.html
│   │   │   │   └── take_quiz.html
│   │   │   └── seturi/
│   │   │       ├── create_set.html
│   │   │       ├── delete_set.html
│   │   │       ├── edit_set.html
│   │   │       ├── home.html
│   │   │       ├── predefined_set.html
│   │   │       ├── predefined_sets.html
│   │   │       ├── read_sets.html
│   │   │       └── view_set.html
│   │   │
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── factories.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── myproject/
│   │   └── urls.py
│   │
│   ├── db.sqlite3
│   └── manage.py
│
├── .gitignore
├── README.md
└── Use Case.jpeg
```

## Cerinte de sistem
- Python 3.10 sau mai nou
- pip
- virtualenv (recomandat)
- Browser web (Chrome, FireFox, Edge)

## Instalare și rulare
1. Clonarea repository-ului:
```bash
git clone <https://github.com/denisaradu28/Flashcard-Web-App.git>
cd Flashcard-Web-App
```
2. Crearea unui virtual environment
```bash
python -m venv .venv
```
3. Activarea virtual environment-ului

Windows:
```bash
.venv\Scripts\activate
```
Linux / macOS:
```bash
source .venv/bin/activate
```
4. Instalarea dependențelor:
```bash
pip install django
```

## Configurare bază de date
```bash
python manage.py makemigrations
python manage.py migrate
```

## Rulare aplicație
```bash
python manage.py runserver
```
Aplicația poate fi accesată la:
```arduino
http://127.0.0.1:8000/seturi/
```

## Funcționalități
- Creare seturi de flashcards
- Editare seturi existente
- Ștergere seturi
- Vizualizare flashcards
- Quiz pentru seturi create de utilizator
- Quiz pentru seturi predefinite
- Salvare progres
- Vizualizare progres (My Progress)

## Seturi predefinite

Seturile predefinite sunt definite în fișierul:
```bash
flashcards/data/predefined_sets.json
```
Acestea sunt încărcate din JSON și nu sunt salvate în baza de date.

## Quiz
- Întrebările sunt afișate una câte una
- Răspunsurile sunt verificate folosind Strategy Pattern
- Utilizatoruș poate sări peste o întrebare
- La final se calculează procentajul de răspunsuri corecte
- Progresul este salvat automat

## My Progress 
- Afișează progresul pentru seturile create de utilizator
- Afișează progresul pentru seturile predefinite
- Datele sunt salvate în tabelul FlashcardProgress

## Autor

Proiect realizat în scop educațional, pentru aprofundarea framework-ului Django și a conceptelor de programare orientată pe obiecte.
