from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify

class UserProfile(models.Model):
    """
    Extends the native Django user model
    Look at https://goo.gl/fwZk1w for further explanation
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    date_of_birth = models.DateField()
    # All the following fields should be chosen from a list of valid inputs
    # on the backend and frontend. In this example they're just comma separated
    # strings
    gender = models.CharField(max_length=255)
    disabilities = models.CharField(max_length=255)
    ethnicity = models.CharField(max_length=255, blank=True)
    current_employer = models.CharField(default="Unemployed", max_length=255, blank=True)

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

class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50, unique=True)
    attributes = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        return u'%s' % (self.name)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name.replace(' ', ''))
        if (len(type(self).objects.filter(slug=self.slug)) != 0):
            raise ValueError("Tag is not unique")

        super(Tag, self).save(*args, **kwargs)

class Question(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    answer = models.TextField(blank=True)
    tags = models.ForeignKey(Tag)
    number_of_views = models.IntegerField(default=0)

    def __unicode__(self):
        return u'%s' % (self.title)
