from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django import forms

from .models import FlashcardSet, Flashcard, FlashcardProgress
from .strategies.exact_match import ExactMatchStrategy
from .strategies.quiz_evaluator import QuizEvaluator
from .services.predefined_loader import PredefinedLoader


def predefined_list(request):
    sets = PredefinedLoader.load_sets()
    return render(request, "seturi/predefined_sets.html", {"sets": sets})


def predefined_set(request, set_key):
    sets = PredefinedLoader.load_sets()

    if set_key not in sets:
        raise Http404("Set not found")

    selected_set = sets[set_key]
    return render(
        request,
        "seturi/predefined_set.html",
        {
            "key": set_key,
            "title": selected_set["title"],
            "cards": selected_set["cards"],
        },
    )


class FlashcardSetForm(forms.ModelForm):
    class Meta:
        model = FlashcardSet
        fields = ["name"]

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("The set name cannot be empty")

        if FlashcardSet.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Set name already exists")

        return name


def home(request):
    return render(request, "seturi/home.html")


def read_sets(request):
    sets = FlashcardSet.objects.all()
    return render(request, "seturi/read_sets.html", {"sets": sets})


def view_set(request):
    set_name = request.GET.get("set_name")
    if not set_name:
        messages.error(request, "No set selected.")
        return redirect("read_sets")

    set_obj = get_object_or_404(FlashcardSet, name=set_name)
    cards = Flashcard.objects.filter(set=set_obj)

    return render(request, "seturi/view_set.html", {"set": set_obj, "cards": cards})


def create_set(request):
    if request.method == "POST":
        form = FlashcardSetForm(request.POST)
        if form.is_valid():
            new_set = form.save()

            questions = request.POST.getlist("question")
            answers = request.POST.getlist("answer")

            for q, a in zip(questions, answers):
                if q.strip() and a.strip():
                    Flashcard.objects.create(set=new_set, question=q, answer=a)

            return redirect("read_sets")
    else:
        form = FlashcardSetForm()

    return render(request, "seturi/create_set.html", {"form": form})


def edit_set(request):
    set_name = request.GET.get("set_name") if request.method == "GET" else request.POST.get("set_name")
    set_obj = FlashcardSet.objects.filter(name=set_name).first()

    if not set_obj:
        messages.error(request, "Set not found")
        return redirect("read_sets")

    cards = Flashcard.objects.filter(set=set_obj)

    if request.method == "POST":
        new_name = request.POST.get("new_name", "").strip()

        if not new_name:
            messages.error(request, "Name cannot be empty")
            return redirect(f"/seturi/set/edit/?set_name={set_name}")

        if FlashcardSet.objects.filter(name__iexact=new_name).exclude(pk=set_obj.pk).exists():
            messages.error(request, "Name already exists")
            return redirect(f"/seturi/set/edit/?set_name={set_name}")

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

        new_questions = request.POST.getlist("new_question")
        new_answers = request.POST.getlist("new_answer")

        for q, a in zip(new_questions, new_answers):
            if q.strip() and a.strip():
                Flashcard.objects.create(set=set_obj, question=q, answer=a)

        messages.success(request, "Set updated successfully")
        return redirect("view_set")

    return render(request, "seturi/edit_set.html", {"set": set_obj, "cards": cards})


def delete_set(request):
    if request.method == "POST":
        set_name = request.POST.get("set_name")
        set_obj = get_object_or_404(FlashcardSet, name=set_name)
        set_obj.delete()
        messages.success(request, f"Set {set_name} was deleted successfully.")
        return redirect("read_sets")

    sets = FlashcardSet.objects.all()
    return render(request, "seturi/delete_set.html", {"sets": sets})


def pre_quiz_start(request, set_key):
    sets = PredefinedLoader.load_sets()

    if set_key not in sets:
        raise Http404("Set not found")

    request.session["pre_quiz"] = {
        "cards": sets[set_key]["cards"],
        "current": 0,
        "finished": False,
        "correct_count": 0,
        "set_key": set_key,
    }

    return redirect("pre_take_quiz")

def get_session_key(request):
    if not request.session.session_key:
        request.session.save()   # creează session în DB și generează cheia
    return request.session.session_key


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
        user_answer = request.POST.get("answer", "").strip()
        evaluator = QuizEvaluator(ExactMatchStrategy())
        correct_answer = (card.get("answer") or "").strip()
        is_correct = evaluator.evaluate(correct_answer, user_answer)
        status = "correct" if is_correct else "incorrect"

        if is_correct:
            quiz["correct_count"] += 1
        request.session["pre_quiz"] = quiz

    return render(
        request,
        "quiz/predefined_take_quiz.html",
        {"card": card, "status": status, "index": index, "total": len(cards)},
    )


def pre_quiz_skip(request):
    quiz = request.session.get("pre_quiz")
    quiz["current"] += 1
    request.session["pre_quiz"] = quiz

    if quiz["current"] >= len(quiz["cards"]):
        return redirect("pre_quiz_finished")

    return redirect("pre_take_quiz")


def pre_quiz_finished(request):
    quiz = request.session.get("pre_quiz")

    if quiz:
        set_key = quiz["set_key"]
        total = len(quiz["cards"])
        correct = quiz.get("correct_count", 0)
        percentage = round(correct / total * 100, 2) if total else 0

        sk = get_session_key(request)

        FlashcardProgress.objects.update_or_create(
            session_key=sk,
            predefined_key=set_key,
            defaults={
                "completed": correct,
                "total": total,
                "percentage": percentage,
            }
        )

        del request.session["pre_quiz"]

    return redirect("my_progress")

def pre_quiz_stop(request):
    quiz = request.session.get("pre_quiz")

    if quiz:
        quiz["finished"] = True
        request.session["pre_quiz"] = quiz

    return redirect("pre_quiz_finished")

def start_quiz(request):
    set_name = request.GET.get("set_name")
    flashcard_set = get_object_or_404(FlashcardSet, name=set_name)

    card_ids = list(flashcard_set.cards.values_list("id", flat=True))

    request.session["quiz_state"] = {
        "set_id": flashcard_set.id,
        "card_ids": card_ids,
        "current_index": 0,
        "correct_count": 0,
        "finished": False,
    }

    return redirect("take_quiz")


def take_quiz(request):
    quiz = request.session.get("quiz_state")

    if not quiz:
        return redirect("home")

    if quiz.get("finished"):
        return redirect("quiz_finished")

    card_id = quiz["card_ids"][quiz["current_index"]]
    card = get_object_or_404(Flashcard, id=card_id)
    status = None

    if request.method == "POST":
        user_answer = request.POST.get("answer", "").strip()
        evaluator = QuizEvaluator(ExactMatchStrategy())
        correct_answer = (card.answer or "").strip()
        is_correct = evaluator.evaluate(correct_answer, user_answer)

        status = "correct" if is_correct else "incorrect"
        if is_correct:
            quiz["correct_count"] += 1

        request.session["quiz_state"] = quiz

    return render(
        request,
        "quiz/take_quiz.html",
        {
            "card": card,
            "status": status,
            "current_index": quiz["current_index"],
            "total_cards": len(quiz["card_ids"]),
        },
    )


def quiz_skip(request):
    quiz = request.session.get("quiz_state")
    if not quiz:
        return redirect("home")

    quiz["current_index"] += 1

    if quiz["current_index"] >= len(quiz["card_ids"]):
        quiz["finished"] = True
        request.session["quiz_state"] = quiz
        return redirect("quiz_finished")

    request.session["quiz_state"] = quiz
    return redirect("take_quiz")


def quiz_finished(request):
    quiz = request.session.get("quiz_state")

    if quiz:
        total = len(quiz["card_ids"])
        correct = quiz["correct_count"]
        percentage = round((correct / total) * 100, 2) if total else 0

        flashcard_set = get_object_or_404(FlashcardSet, id=quiz["set_id"])
        sk = get_session_key(request)

        FlashcardProgress.objects.update_or_create(
            session_key=sk,
            set_id=quiz["set_id"],
            defaults={
                "completed": correct,
                "total": total,
                "percentage": percentage,
            },
        )

        del request.session["quiz_state"]

    return redirect("my_progress")

def quiz_stop(request):
    quiz = request.session.get("quiz_state")

    if quiz:
        quiz["finished"] = True
        request.session["quiz_state"] = quiz

    return redirect("quiz_finished")

def my_progress(request):
    sk = get_session_key(request)
    progress_list = FlashcardProgress.objects.filter(session_key=sk).select_related("set")
    return render(request, "progress/my_progress.html", {"progress_list": progress_list})
