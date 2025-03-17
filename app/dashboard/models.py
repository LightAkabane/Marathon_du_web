from django.db import models

class UserData(models.Model):
    user_id = models.CharField(max_length=100)
    page_views = models.IntegerField(default=0)
    session_duration = models.IntegerField(default=0)  # En secondes
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user_id
    
class LyceeData(models.Model):
    user_id = models.CharField(max_length=100)
    lycee_name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    profile_type = models.CharField(max_length=100)
    usage_purpose = models.CharField(max_length=100)  # "actualité" ou "documentation"
    articles_visited = models.TextField()             # On stocke la liste d'articles sous forme de texte
    page_views = models.IntegerField()
    session_duration = models.IntegerField()
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.user_id} - {self.lycee_name}"