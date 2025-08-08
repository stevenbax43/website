from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class adress(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    author_id = models.ForeignKey(User, default=None, on_delete=models.SET_NULL, null=True) 
    date = models.DateTimeField(auto_now_add=True)
    pcode = models.CharField(max_length=6)
    hnumber= models.CharField(max_length=6)
    addition=   models.CharField(max_length=4, blank = True) #black is true betekent dat the field is allowed to be blank
    street= models.TextField()
    place=  models.TextField()
    EP_label= models.TextField(max_length=5,default='')
    EP_surface = models.TextField(max_length=5, default='')
    EP_energie= models.TextField(max_length=5, default='')
    EP_PrimEnergie= models.TextField(max_length=5, default='')
    EP_gebouwklasse = models.TextField(max_length=5, default='')
    EP_TO = models.TextField(max_length=5, default='')
    EP_warmte = models.TextField(max_length=5, default='')
    BAG_surface= models.PositiveIntegerField(default='')
    buildyear= models.PositiveIntegerField(default='')
    purpose= models.TextField()
    calendaryear= models.PositiveIntegerField(default='2017')
    elektra= models.PositiveIntegerField(default='0')
    elektra_terug = models.PositiveIntegerField(default='0',blank = True)
    gas= models.PositiveIntegerField(default='0')
    weii = models.TextField(max_length=20)

    #To see all instances, created in the model database, by title rather than obj1, obj2 etc..,
    # To see all instances, created in the model database, by title rather than obj1, obj2 etc..,
    def __str__(self):
        return f"{self.pcode} - {self.hnumber}"

class ProjectMollier(models.Model):
    user           = models.ForeignKey(User, on_delete=models.CASCADE)
    projectname    = models.CharField(max_length=255)
    sessionstorage = models.JSONField()
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: {self.projectname} ({self.user.username})"