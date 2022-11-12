from django.db import models

# Create your models here.
class DiscordBreakUser(models.Model):
    id = models.BigAutoField(
        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
    )
    name = models.CharField(max_length=10)
    total_break = models.IntegerField()
    today_break = models.IntegerField()
    total_input = models.IntegerField()
    today_input = models.IntegerField()
    last_input = models.DateTimeField(auto_now_add=True)