#from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings

class FlashcardSet(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Flashcard(models.Model):
    set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='cards')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class FlashcardProgress(models.Model):
    session_key = models.CharField(max_length=100, db_index=True)
    set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, null=True, blank=True)
    predefined_key = models.CharField(max_length=50, null=True, blank=True)
    completed = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session_key", "set"], name="uniq_progress_session_set"),
            models.UniqueConstraint(fields=["session_key", "predefined_key"], name="uniq_progress_session_predef"),
        ]

    def __str__(self):
        if self.set:
            return f"User set: {self.set.name}"
        return f"Predefined set: {self.predefined_key}"