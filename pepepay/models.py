from django.db import models


class Users(models.Model):
    image_url = models.ImageField(upload_to='images/', null=True)
    firstname = models.CharField(max_length=30, blank=False, null=False)
    lastname = models.CharField(max_length=30, blank=False, null=False)
    email = models.EmailField()
    password = models.CharField(max_length=100, blank=False, null=True)
    number = models.CharField(max_length=30, blank=False, null=False)
    address = models.CharField(max_length=100, blank=False, null=False)
    country = models.CharField(max_length=50, blank=False, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Recipients(models.Model):
    firstname = models.CharField(max_length=30, blank=False, null=False)
    lastname = models.CharField(max_length=30, blank=False, null=False)
    email = models.EmailField()
    useremail = models.EmailField()

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Transactions(models.Model):
    name = models.CharField(max_length=230, blank=False, null=False)
    sendername = models.CharField(max_length=230, blank=False, null=False)
    description = models.CharField(max_length=30, blank=False, null=False)
    email = models.EmailField(null=True)
    senderemail = models.EmailField(null=True, blank=True)
    recipientemail = models.EmailField(null=True)
    status = models.CharField(max_length=230, blank=False, null=False)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.CharField(max_length=230, blank=False, null=False)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


class Notifications(models.Model):
    notification = models.CharField(max_length=260, blank=True, null=True)
    url = models.CharField(max_length=30, blank=False, null=False)
    useremail = models.EmailField(null=True)
    time = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=230, blank=False, null=True)
    recipientemail = models.EmailField(null=True)
    senderemail = models.EmailField(null=True)
    amount = models.CharField(max_length=30, blank=False, null=True)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
