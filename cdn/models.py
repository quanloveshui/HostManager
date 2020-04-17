from django.db import models

# Create your models here.

class Student(models.Model):
    name = models.CharField(max_length=20)
    age = models.IntegerField(max_length=3)

    def __unicode__(self):
        return self.name


class Subject(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    sub_name = models.CharField(max_length=20)
    sub_num = models.IntegerField(default=0)

    def __unicode__(self):
        return self.sub_name

class Nodeinfo(models.Model):
    name = models.CharField('主机名',max_length=32)
    ip_address = models.GenericIPAddressField('IP地址', blank=True, null=True)
    province = models.CharField('省份',max_length=32)
    city = models.CharField('城市', max_length=32)
    isp = models.CharField('运营商', max_length=32)
    machineagent = models.CharField('代理商', max_length=32)
    vip = models.GenericIPAddressField('VIP地址', blank=True, null=True)

    def __str__(self):
        return self.name
