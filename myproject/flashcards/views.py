from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

# Create your views here.
from .models import FlashcardSet, Flashcard
from django import forms

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


def create_set(request):
    if request.method == 'POST':
        form = FlashcardSetForm(request.POST)
        if form.is_valid():
            new_set = form.save()

            questions = request.POST.getlist('question')
            answers = request.POST.getlist('answer')

            for q, a in zip(questions, answers):
                if q.strip() and a.strip():
                    FlashcardSet.objects.create(set=new_set, question=q, answer=a)

            return redirect('read_sets')
    else:
        form = FlashcardSetForm()

    return render(request, 'seturi/create_set.html', {'form': form})


def read_sets(request):
    sets = FlashcardSet.objects.all()
    return render(request, 'seturi/read_sets.html', {'sets': sets})


def edit_set(request):
    sets = FlashcardSet.objects.all()

    if request.method == 'POST':
        set_name = request.POST.get('set_name')
        new_name = request.POST.get('new_name')

        set_obj = FlashcardSet.objects.filter(name=set_name).first()
        if not set_obj:
            messages.error(request, 'Set not found')
            return redirect('create_set')

        if not new_name.strip():
            messages.error(request, 'New set name cannot be empty')
        elif FlashcardSet.objects.filter(name__iexact=new_name).exclude(pk=set_obj.pk).exists():
            messages.error(request, 'Set name already exists')
        else:
            set_obj.name = new_name
            set_obj.save()
            messages.success(request, f'Set \"{set_obj.name}\" was updated successfully')
            return redirect('read_sets')

    return render(request, 'seturi/edit_set.html', {'sets': sets})


def delete_set(request):
    if request.method == 'POST':
        set_name = request.POST.get('set_name')
        set_obj = get_object_or_404(FlashcardSet, name=set_name)
        set_obj.delete()
        messages.success(request, f'Set {set_name} was deleted successfully.')
        return redirect('read_sets')
    sets = FlashcardSet.objects.all()
    return render(request, 'seturi/delete_set.html', {'sets': sets})