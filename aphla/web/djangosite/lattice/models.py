from django.db import models

# Create your models here.

class Channel(models.Model):
    pv          = models.CharField(max_length=64)
    elemName    = models.CharField(max_length=16)
    cell        = models.CharField(max_length=4)
    girder      = models.CharField(max_length=4)
    #elemIndex   = models.IntegerField()
    devName     = models.CharField(max_length=32)
    dev_name    = models.CharField(max_length=32)
    elemField   = models.CharField(max_length=32)
    elemGroup   = models.CharField(max_length=64)
    elemHandle  = models.CharField(max_length=32)
    #elemLength  = models.FloatField()
    #elemPolar   = models.IntegerField()
    #elemPosition= models.FloatField()
    elemType    = models.CharField(max_length=32)
    girder      = models.CharField(max_length=32) 
    hostName    = models.CharField(max_length=32)
    iocName     = models.CharField(max_length=32)
    system      = models.CharField(max_length=32)
    tags        = models.CharField(max_length=32)

    class Meta:
        db_table = 'channels'
