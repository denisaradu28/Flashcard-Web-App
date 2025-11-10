#from django.db import models

# Create your models here.
from django.db import models

class FlashcardSet(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Flashcard(models.Model):
    set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='cards', null = True)
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question
