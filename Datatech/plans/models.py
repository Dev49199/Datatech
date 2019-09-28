from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Article(models.Model):
	title = models.CharField(max_length=40)
	Text = models.TextField()
	premium = models.BooleanField()




class Customer(models.Model):
	user = models.OneToOneField(User,on_delete=models.CASCADE)
	stripeid = models.CharField(max_length=255)
	stripe_subscription_id = models.CharField(max_length = 255)
	cancel_at_period_end = models.BooleanField(default = False)
	membership = models.BooleanField(default=False)