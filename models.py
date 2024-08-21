from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import django_filters

STATUS=(
    ('P','Pending'),
    ('I','In Progress'),
    ('C','Completed'),
)

class Problem(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=1000)
    updated_at = models.DateTimeField(auto_now=True)
    assign_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_problems')
    status = models.CharField(max_length=1,choices= STATUS)
    remark= models.CharField(max_length=100, null=True) 

    def __str__(self):
        return self.title + '/n' +self.description
    
    @classmethod
    def problems_solved_in_last_24_hours(cls, user):
        since = timezone.now() - timezone.timedelta(hours=24)
        return cls.objects.filter(assign_to=user, status='C', updated_at__gte=since).count()

    @classmethod
    def problems_solved_in_last_month(cls, user):
        since = timezone.now() - timezone.timedelta(days=30)
        return cls.objects.filter(assign_to=user, status='C', updated_at__gte=since).count()

    @classmethod
    def total_problems_solved(cls, user):
        return cls.objects.filter(assign_to=user, status='C').count()
    
class Notification(models.Model):
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_notifications', on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.message
    
class ProblemFilter(django_filters.FilterSet):
    class Meta:
        model = Problem
        fields= ['created_at','status']

class ProblemUpdate(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    update_status= models.CharField(max_length=1,choices= STATUS)
    update_assign= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_problem')
    update_description = models.TextField()
    updated_at = models.DateTimeField(auto_now_add=True)
    check_description = models.BooleanField(default=False)
    check_status = models.BooleanField(default=False)
    check_assign = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.updated_by.username} - {self.update_description[:30]} - {self.updated_at}"
    
@receiver(post_save, sender=Problem)
def create_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.assign_to,
            sender=instance.created_by,
            message=f'A new problem "{instance.title}" has been assigned to you.'
        )
    elif instance.status == 'I':
        Notification.objects.create(
            recipient=instance.created_by,
            sender=instance.assign_to,
            message=f'The problem "{instance.title}" is now in progress.'
        )
    elif instance.status == 'C':
        Notification.objects.create(
            recipient=instance.created_by,
            sender=instance.assign_to,
            message=f'The problem "{instance.title}" has been completed.'
        )
