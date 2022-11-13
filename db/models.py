from django.db import models

# Create your models here.
class UsersOnBreak(models.Model):
    id = models.BigAutoField(
        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
    )
    name = models.CharField(max_length=20)
    nickname = models.CharField(max_length=100)
    discriminator = models.CharField(max_length=4)
    total_break = models.IntegerField(default=0)
    today_break = models.IntegerField(default=0)
    total_input = models.IntegerField(default=0)
    today_input = models.IntegerField(default=0)
    is_resting = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    remaining_rest_time = models.IntegerField(default=0)
