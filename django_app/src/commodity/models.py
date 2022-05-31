from django.db import models

# Create your models here.
from django.urls import reverse


class MyModel(models.Model):
    # file will be uploaded to MEDIA_ROOT/uploads
    upload = models.FileField(upload_to='uploads/')
    # or...
    # file will be saved to MEDIA_ROOT/uploads/2015/01/30
    upload = models.FileField(upload_to='uploads/%Y/%m/%d/')

class ObjectDetect(models.Model):
    img1 = models.ImageField('Image 1')
    img2 = models.ImageField('Image 2')
    name = models.CharField(default="ObjectDetect", max_length=200)
    createdate = models.DateTimeField('Date Created', auto_now_add=True)
    config = models.JSONField(default=None, null=True)
    out1 = models.ImageField(default=None, )
    out2 = models.ImageField(default=None, )
    outstring = models.CharField(default="", max_length=2000)


    def __str__(self):
        return self.name
        # return self.name + str(self.createdate)

    # def get_absolute_url(self):
    #     return reverse('upload:index')

from django.contrib.auth.models import User
from django.db import models

# class Author(models.Model):
#     name = models.CharField(max_length=200)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class CommodityDetect(models.Model):
    Name = models.CharField(default="CommodityDetect", max_length=200)
    ConfigJson = models.JSONField(null=True)
    Img1 = models.ImageField()
    Img2 = models.ImageField()
    Img1Result = models.ImageField()
    Img2Result = models.ImageField()
    Date = models.DateTimeField('Date Created', auto_now_add=True)

    # created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # def __str__(self):
    #     return f'{self.name} ({self.id})'

#---------------------------
class Author(models.Model):
    name = models.CharField(max_length=200)

    def get_absolute_url(self):
        return reverse('commodity:author-detail', kwargs={'pk': self.pk})
