from django.db import models

# Create your models here.

default_address_dict = {}

class Vacancy(models.Model):
    company_name = models.CharField(max_length=150)
    job_category = models.CharField(max_length=150)
    job_level = models.CharField(max_length=150)
    no_of_vacancy = models.IntegerField()
    employment_type = models.CharField(max_length=150)
    file = models.FileField(upload_to='vacancy_files', null=True, blank=True)
    salary = models.CharField(max_length=150)
    job_location = models.CharField(max_length=150)
    content = models.TextField(null=True, blank=True)
    apply_before = models.DateField()
    content = models.TextField()
    apply_here_url = models.URLField(max_length=300, blank=True, null=True)
    apply_here_email = models.EmailField(max_length=200, blank=True, null=True)

