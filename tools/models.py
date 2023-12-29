from django.db import models

# Create your models here.
class adress(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    date = models.DateTimeField(auto_now_add=True)
    pcode = models.CharField(max_length=6)
    hnumber= models.CharField(max_length=6)
    addition=   models.CharField(max_length=4)
    street= models.TextField()
    place=  models.TextField()
    EP_label= models.TextField(max_length=5)
    BAG_surface= models.PositiveIntegerField(default='')
    buildyear= models.PositiveIntegerField(default='')
    purpose= models.TextField()
    calendaryear= models.PositiveIntegerField(default='2017')
    elektra= models.PositiveIntegerField(default='0')
    elektra_terug = models.PositiveIntegerField(default='0')
    gas= models.PositiveIntegerField(default='0')
    weii = models.TextField(max_length=20)

    #To see all instances, created in the model database, by title rather than obj1, obj2 etc..,
    # To see all instances, created in the model database, by title rather than obj1, obj2 etc..,
    def __str__(self):
        return f"{self.pcode} - {self.hnumber}"