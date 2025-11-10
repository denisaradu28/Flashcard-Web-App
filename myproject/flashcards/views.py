from django.shortcuts import render, redirect

# Create your views here.
from .models import FlashcardSet
from django import forms

class FlashcardSetForm(forms.ModelForm):
    class Meta:
        model = FlashcardSet
        fields = ['name']

def create_set(request):
    if request.method == 'POST':
        form = FlashcardSetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('read_sets')
    else:
        form = FlashcardSetForm()

    return render(request, 'seturi/create_set.html', {'form': form})


def read_sets(request):
    sets = FlashcardSet.objects.all()
    return render(request, 'seturi/read_sets.html', {'sets': sets})