from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from rest_framework.authtoken.models import Token
from django.utils.text import slugify
from django.core.exceptions import ValidationError

gender_options = (('male', 'Male'), ('female', 'Female'))
profile_attributes = (
    ('gender', 'Gender'), ('ethnicity', 'Ethnicity'), ('position', 'Position'),
    ('current_employer', 'Current Employer'))

class Tag(models.Model):
    slug = models.CharField(max_length=50, unique=True)
    attribute = models.CharField(max_length=100, choices=profile_attributes)
    value = models.CharField(max_length=100)

    def __unicode__(self):
        return u'%s' % (self.value)

    def clean(self):
        self.slug = slugify((self.attribute + self.value).replace(' ', ''))
        if (len(type(self).objects.filter(slug=self.slug)) != 0):
            raise ValidationError("Tag is not unique")
        return self

class Question(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    number_of_views = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s' % (self.title)

class UserProfile(models.Model):
    """
    Extends the native Django user model
    Look at https://goo.gl/fwZk1w for further explanation
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()

    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=255, choices=gender_options)
    disabilities = models.CharField(max_length=255)
    ethnicity = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255, blank=True)
    current_employer = models.CharField(max_length=255, blank=True)
    bookmarks = models.ManyToManyField(Question)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='')

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def save(self, *args, **kwargs):
       self.pk = self.user.pk
       super(UserProfile, self).save(*args, **kwargs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
   """
   Receiver is a decorator that activates an action when the native
   django user model has been saved. This lets us create a matching
   (empty) UserProfile whenever a user is created
   """
   if created and not instance.is_superuser:
       UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if not instance.is_superuser:
        instance.userprofile.save()

@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

class Employer(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=0, default=0)
    averagesalary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    questions = models.ManyToManyField(Question)
