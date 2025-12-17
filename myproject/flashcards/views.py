from functools import total_ordering

from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import FlashcardSet, Flashcard, FlashcardProgress
from django import forms
from .factories import UserFlashcardSetCreator, CardDTO
predefined_sets = {
    "POO": {
        "title": "POO Basisc",
        "cards": [
            {"question": "Ce este un obiect?", "answer": "O instanta a unei clase."},
            {"question": "Ce este o clasa?", "answer": "Un sablon pentru crearea obiectelor."},
            {"question": "Ce este mostenirea", "answer": "Mecanismul prin care o clasa preia proprietati si metode din alta clasa."},
            {"question": "Ce este polimorfismul?", "answer": "Capacitatea aceleiasi metode de a se comporta diferit in functie de context."},
            {"question": "Ce este o interfata?", "answer": "Un tip care defineste doar metode fara implementare."},
            {"question": "Ce este overriding-ul?", "answer": "Redefinirea unei metode mostenite in clasa copil."},
            {"question": "Ce este overloading-ul?", "answer": "Definirea mai multor metode cu acelasi nume, dar parametri diferiti."}
        ]
    },
    "python": {
        "title": "Python Basics",
        "cards": [
            {"question": "Ce este o lista in Python?", "answer": "O colectie ordonata si modificabila de elemente."},
            {"question": "Ce este 'None'?", "answer": "O constanta care reprezinta absenta unei valori."},
            {"question": "Ce este un modul?", "answer": "Un fisier Python ce contine variabile, functii sau clase reutilizabile."},
            {"question": "Ce este un dictionar?", "answer": "O colectie de perechi cheie-valoare."},
            {"question": "Ce face functia pop()?", "answer": "Sterge si returneaza ultimul elemnet din lista."},
            {"question": "Ce tip de date returneaza functia input()?", "answer": "Intotdeauna un string."},
            {"question": "Ce este list comprehension?", "answer": "O metoda scurta de a crea liste folosind expresii."}
        ]
    },
    "cyber": {
        "title": "Cybersecurity",
        "cards": [
            {"question": "Ce este cybersecurity?", "answer": "Protejarea sistemelor si datelor impotriva atacurilor."},
            {"question": "Ce este un firewall?", "answer": "Un sistem care filtreaza traficul de retea."},
            {"question": "Ce este malware?", "answer": "Software malitios creat pentru a provoca daune"},
            {"question": "Ce este autentificare?", "answer": "Procesul prin care se verifica identitatea unui utilizator."},
            {"question": "Ce este un atac DDoS?", "answer": "Suprasolicitarea unui server cu trafic pentru a-l bloca."},
            {"question": "Ce este hashing-ul?", "answer": "Transformarea datelor intr-o valoare fixa, ireversibila."}
        ]
    },

    "so": {
        "title": "Sisteme de operare",
        "cards": [
            {"question": "Ce este un sistem de operare?", "answer": "Software care gestioneaza hardware-ul si ruleazaa aplicatiile."},
            {"question": "Ce este un thread?", "answer": "Cea mai mica unitate de executie dintr-un proces."},
            {"question": "Ce este memoria virtuala?", "answer": "Tehnica ce permite folosirea discului ca extensie a RAM-ului."},
            {"question": "Ce este kernel-ul?", "answer": "Componenta centrala a sistemului de operare."},
            {"question": "Ce este un deadlock?", "answer": "Situatie in care procesele se blocheaza reciproc."},
            {"question": "Ce este un sistem de fisiere?", "answer": "Structura prin care OS-ul organizeaza si stocheaza fisierele."}
        ]
    }

}

def predefined_list(request):
    return render(request, "seturi/predefined_sets.html", {
        "sets": predefined_sets
    })

def predefined_set(request, set_key):
    if set_key not in predefined_sets:
        raise Http404("Set not found")

    selected_set = predefined_sets[set_key]
    return render(request, "seturi/predefined_set.html",{
        "key": set_key,
        "title": selected_set["title"],
        "cards": selected_set["cards"],
    })



class FlashcardSetForm(forms.ModelForm):
    class Meta:
        model = FlashcardSet
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
                raise forms.ValidationError("The set name cannot be empty")

        existing = FlashcardSet.objects.filter(name__iexact=name)
        if self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        if existing.exists():
            raise forms.ValidationError("Set name already exists")

        return name


def home(request):
    return render(request, 'seturi/home.html')

def create_set(request):
    if request.method == 'POST':
        form = FlashcardSetForm(request.POST)
        if form.is_valid():
            new_set = form.save()

            name = form.cleaned_data['name']
            question = request.POST.getlist("question")
            answer = request.POST.getlist("answer")

            cards = [CardDTO(q,a) for q, a in zip(question, answer)]

            creator = UserFlashcardSetCreator(name=name, cards=cards)
            #creator.create_set()

            return redirect('read_sets')

            # questions = request.POST.getlist('question')
            # answers = request.POST.getlist('answer')
            #
            # for q, a in zip(questions, answers):
            #     if q.strip() and a.strip():
            #         Flashcard.objects.create(set=new_set, question=q, answer=a)
            #
            # return redirect('read_sets')
    else:
        form = FlashcardSetForm()

    return render(request, 'seturi/create_set.html', {'form': form})


def read_sets(request):
    sets = FlashcardSet.objects.all()
    return render(request, 'seturi/read_sets.html', {'sets': sets})


def edit_set(request):
    set_name = request.GET.get('set_name') if request.method == 'GET' else request.POST.get('set_name')

    set_obj = FlashcardSet.objects.filter(name=set_name).first()
    if not set_obj:
        messages.error(request, 'Set not found')
        return redirect('read_sets')

    cards = Flashcard.objects.filter(set=set_obj)

    if request.method == 'POST':
        new_name = request.POST.get('new_name')

        if not new_name.strip():
            messages.error(request, 'Name cannot be empty')
            return redirect(f'/seturi/set/edit/?set_name={set_name}')

        if FlashcardSet.objects.filter(name__iexact=new_name).exclude(pk=set_obj.pk).exists():
            messages.error(request, 'Name already exists')
            return redirect(f'/seturi/set/edit/?set_name={set_name}')

        set_obj.name = new_name
        set_obj.save()

        for card in cards:
            if request.POST.get(f"delete_{card.id}"):
                card.delete()
                continue

            q = request.POST.get(f"question_{card.id}")
            a = request.POST.get(f"answer_{card.id}")

            if q and a:
                card.question = q
                card.answer = a
                card.save()

        new_questions = request.POST.getlist('new_question')
        new_answers = request.POST.getlist('new_answer')

        for q, a in zip(new_questions, new_answers):
            if q.strip() and a.strip():
                Flashcard.objects.create(set=set_obj, question=q, answer=a)

        messages.success(request, 'Set updated successfully')
        return redirect('view_set')

    return render(request, 'seturi/edit_set.html', {
        "set": set_obj,
        "cards": cards
    })

def delete_set(request):
    if request.method == 'POST':
        set_name = request.POST.get('set_name')
        set_obj = get_object_or_404(FlashcardSet, name=set_name)
        set_obj.delete()
        messages.success(request, f'Set {set_name} was deleted successfully.')
        return redirect('read_sets')
    sets = FlashcardSet.objects.all()
    return render(request, 'seturi/delete_set.html', {'sets': sets})

def view_set(request):
    set_name = request.GET.get('set_name') or request.GET.get('set_name')

    if not set_name:
        messages.error(request, 'No set selected.')
        return redirect('read_sets')

    set_obj = get_object_or_404(FlashcardSet, name=set_name)
    cards = Flashcard.objects.filter(set=set_obj)

    return render(request, 'seturi/view_set.html', {"set": set_obj, "cards": cards})

def pre_quiz_start(request, set_key):
    if set_key not in predefined_sets:
        raise Http404("Set not found")

    selected_set = predefined_sets[set_key]["cards"]

    request.session["pre_quiz"] = {
        "cards": selected_set,
        "current": 0,
        "finished": False,
        "set_key": set_key
    }

    return redirect("pre_take_quiz")

def pre_take_quiz(request):
    quiz = request.session.get("pre_quiz")

    if not quiz or quiz["finished"]:
        return redirect("predefined_list")

    index = quiz["current"]
    cards = quiz["cards"]

    if index >= len(cards):
        return redirect("pre_quiz_finished")

    card = cards[index]

    status = None

    if request.method == "POST":
        user_answer = request.POST.get("answer", "").strip().lower()
        correct_answer = card["answer"].strip().lower()

        if user_answer == correct_answer:
            status = "correct"
        else:
            status = "incorrect"

    return render(request, "quiz/predefined_take_quiz.html", {
        "card": card,
        "status": status,
        "index": index,
        "total": len(cards)
    })

def pre_quiz_skip(request):
    quiz = request.session.get("pre_quiz")

    if not quiz:
        return redirect("predefined_list")

    quiz["current"] += 1
    request.session["pre_quiz"] = quiz

    if quiz["current"] >= len(quiz["cards"]):
        return redirect("pre_quiz_finished")

    return redirect("pre_take_quiz")

def pre_quiz_stop(request):
    quiz = request.session.get("pre_quiz")

    if quiz:
        quiz["finished"] = True
        request.session["pre_quiz"] = quiz

    return redirect("pre_quiz_finished")

def pre_quiz_finished(request):
    try:
        del request.session["pre_quiz"]
    except KeyError:
        pass

    return render(request, "quiz/quiz_finished.html")


def start_quiz(request):
    set_name = request.GET.get("set_name")

    if not set_name:
        return redirect("home")

    flashcard_set = get_object_or_404(FlashcardSet, name=set_name)

    card_ids = list(flashcard_set.cards.values_list("id", flat=True))

    if not card_ids:
        return render(request, "quiz/no_cards.html",{"set": flashcard_set})

    request.session["quiz_state"] ={
        "set_id": flashcard_set.id,
        "card_ids": card_ids,
        "current_index": 0,
        "finished": False,
    }

    return redirect("take_quiz")

def take_quiz(request):
    quiz = request.session.get("quiz_state")

    if not quiz or quiz.get("finished"):
        return redirect("home")

    card_ids = quiz["card_ids"]
    current_index = quiz["current_index"]

    if current_index >= len(card_ids):
        return redirect("quiz_finished")

    card_id = card_ids[current_index]
    card = get_object_or_404(Flashcard, id=card_id)

    status = None

    if request.method == "POST":
        user_answer = request.POST.get("answer","").strip()
        correct_answer = (card.answer or "").strip()

        if user_answer != "":

            if user_answer.lower() == correct_answer.lower():
                status = "correct"
                quiz["correct_count"] = quiz.get("correct_count", 0) + 1
            else:
                status = "incorrect"
        else:
            status = None
        request.session["quiz_state"] = quiz


    context = {
        "set_id": quiz["set_id"],
        "card": card,
        "current_index": current_index,
        "total_cards": len(card_ids),
        "status": status,
    }

    return render(request, "quiz/take_quiz.html", context)

def quiz_skip(request):
    quiz = request.session.get("quiz_state")

    if not quiz or quiz.get("finished"):
        return redirect("home")

    quiz["current_index"] += 1

    if quiz["current_index"] >= len(quiz["card_ids"]):
        quiz["finished"] = True
        request.session["quiz_state"] = quiz
        return redirect("quiz_finished")

    request.session["quiz_state"] = quiz
    return redirect("take_quiz")

def quiz_stop(request):
    quiz = request.session.get("quiz_state")

    if quiz:
        quiz["finished"] = True
        request.session["quiz_state"] = quiz

    return redirect("quiz_finished")

def quiz_finished(request):
    quiz = request.session.get("quiz_state")

    # if "quiz_state" in request.session:
    #     del request.session["quiz_state"]
    #
    # return render(request, "quiz/quiz_finished.html", {"quiz": quiz})

    if quiz:
        set_id = quiz.get("set_id")
        set_obj = FlashcardSet.objects.get(id=set_id)

        #completed = quiz.get("current_index", 0)
        total = len(quiz.get("card_ids", []))
        correct = quiz.get("correct_count", 0)


        parcentage = round((correct / total) * 100, 2) if total > 0 else 0

        FlashcardProgress.objects.update_or_create(
            set=set_obj,
            defaults={
                "completed": correct,
                "total": total,
                "percentage": parcentage,
            }
        )

        del request.session["quiz_state"]

    return render(request, "quiz/quiz_finished.html")

def my_progress(request):
    progress_list = FlashcardProgress.objects.all()

    return render(request, "progress/my_progress.html", {"progress_list": progress_list})