from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

    
class Record(models.Model):
    title = models.CharField(max_length=50)
    recording = models.FileField(upload_to='recordings/')
    tempo = models.IntegerField(default=100,
        validators=[
            MaxValueValidator(120),
            MinValueValidator(20)
        ])
    uploaded_at = models.DateTimeField(auto_now_add=True)

class ABCSong(models.Model):
    title = models.CharField(max_length=50, blank=True)
    time_sig = models.CharField(max_length=5, default="4/4")
    length = models.CharField(max_length=5, default="1/4")
    key = models.CharField(max_length=4, default="Dmaj")
    song = models.CharField(max_length=500)
