from django.db import models

# Create your models here.

class Role(models.Model):
    name = models.CharField(max_length=32,verbose_name="角色")

    def __str__(self):
        return self.name

class UserGroup(models.Model):
    title = models.CharField(max_length=32)

    def __str__(self):
        return self.title

class UserInfo(models.Model):

    username = models.CharField(max_length=32,verbose_name="用户名")
    email = models.CharField(max_length=32,verbose_name="邮箱")
    ug = models.ForeignKey("UserGroup",null=True,blank=True,verbose_name="用户组")
    m2m = models.ManyToManyField("Role",verbose_name="角色")
    def __str__(self):
        return self.username







