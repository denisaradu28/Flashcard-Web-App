from django.shortcuts import render, redirect, get_object_or_404
from pyexpat.errors import messages

# Create your views here.
from .models import FlashcardSet
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
            form.save()
            return redirect('read_sets')
    else:
        form = FlashcardSetForm()

    return render(request, 'seturi/create_set.html', {'form': form})


def read_sets(request):
    sets = FlashcardSet.objects.all()
    return render(request, 'seturi/read_sets.html', {'sets': sets})


def edit_set(request, set_id):
    set_obj = get_object_or_404(FlashcardSet, id=set_id)
    if request.method == 'POST':
        form = FlashcardSetForm(request.POST, instance=set_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "The set was successfully updated!")
            return redirect('read_sets')
        else:
            messages.error(request, "Error: please check the entered fields.")
    else:
        form = FlashcardSetForm(instance=set_obj)
    return render(request, 'seturi/edit_set.html', {'form': form, 'set': set_obj})


def delete_set(request):
    if request.method == 'POST':
        set_id = request.POST.get('set_id')
        if not set_id:
            messages.error(request, "Error: invalid set ID.")
            return redirect('read_sets')

        set_obj = get_object_or_404(FlashcardSet, id=set_id)
        set_obj.delete()
        messages.success(request, f"The set '{set_obj.name}' was deleted successfully!")
        return redirect('read_sets')

    messages.error(request, "Invalid request.")
    return redirect('read_sets')
