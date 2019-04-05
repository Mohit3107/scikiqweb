# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.utils import timezone

# Create your models here.
class User(models.Model):
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=254,validators=[MinLengthValidator(8),MaxLengthValidator(20),RegexValidator(regex='^(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$',message='password shall be 8-20 characters, include a number and a special character',code='invalid_password')])
    apikey = models.CharField(max_length=128, blank=True, null=True)
    date_updated = models.DateTimeField(default=timezone.now, blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
    is_delete = models.CharField(max_length =1, choices=(('0','Notdelete'), ('1',"Delete")), default='0')
    
    def __unicode__(self): 
        return  self.email

class UserProfile(models.Model):
    user = models.ForeignKey(User, related_name="profile")
    name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    job = models.CharField(max_length=50,blank=True, null=True)
    company = models.CharField(max_length=100)
    subscription = models.CharField(max_length =1, choices=(('0','OFF'), ('1',"ON")), default='0', blank=True, null=True)
    membership = models.CharField(max_length =1, choices=(('0','Default'), ('1',"Bronze"),('2','Silver'), ('3',"Gold"),('4','Platinum')), default='0', blank=True, null=True)    
    website = models.CharField(max_length=128, blank=True, null=True)
    office_number = models.CharField(max_length=20, blank=True, null=True)
    office_number_isd = models.CharField(max_length=20, blank=True, null=True)
    mobile_number = models.CharField(max_length=20)
    mobile_number_isd = models.CharField(max_length=20)
    date_updated = models.DateTimeField(default=timezone.now, blank=True, null=True)
    companytype = models.CharField(max_length =1, default='0', blank=True, null=True)
    preferred_language = models.CharField(max_length =3, default='0', blank=True, null=True)
    priceformat = models.CharField(max_length =2, default='1', blank=True, null=True)
    timeformat = models.CharField(max_length =2, default='1', blank=True, null=True)
    dateformat = models.CharField(max_length =2, default='1', blank=True, null=True)
    preffered_currency = models.CharField(max_length =2, default='1', blank=True, null=True)
    username = models.CharField(max_length =100)
    customuserid = models.CharField(max_length=50,default='',null=True,blank=True)
    image = models.ImageField(upload_to="images/", null=True,blank=True) 
     
    def __unicode__(self):
        return unicode(self.name)

    def getinfo(self):
        return '{"name":"%s","image":"%s"}' % (self.name,self.image)

    def getEmail(self):
        return '{"id":"%s","email":"%s","email_status":"%s"}'%(self.user_id, self.user.email, self.user.user_verified)

    def getNumber(self):
        return '{"id":"%s","number":"%s"}'%(self.user_id, self.mobile_number)

class CodeVerify(models.Model):
    user = models.ForeignKey(User, related_name="usercode")
    code = models.CharField(max_length=6)
    source = models.CharField(max_length=20)

    def __unicode__(self):
        return self.user.email 