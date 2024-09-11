from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Industry(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class City(models.Model):
    name = models.CharField(max_length=255, default='')
    state = models.ForeignKey('State', on_delete=models.CASCADE,blank=True, null=True, related_name='cities', default=None)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['state']),
        ]

    def __str__(self):
        return f"{self.name}"

class State(models.Model):
    name = models.CharField(max_length=255, default='')
    country = models.ForeignKey('Country', on_delete=models.CASCADE,blank=True, null=True, related_name='states', default=None)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['country']),
        ]

    def __str__(self):
        return f"{self.name}"

class Country(models.Model):
    name = models.CharField(max_length=255, default='')

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

class Company(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    domain = models.CharField(max_length=255, blank=True, null=True)
    year_founded = models.IntegerField(blank=True, null=True)
    industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, blank=True, null=True, related_name='companies')
    size_range = models.CharField(max_length=255, blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True, related_name='companies',default=None)
    linkedin_url = models.URLField(blank=True, null=True)
    current_employee_estimate = models.IntegerField(blank=True, null=True)
    total_employee_estimate = models.IntegerField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['city']),
            models.Index(fields=['industry']),
            models.Index(fields=['size_range']),
        ]

    def __str__(self):
        return f"{self.name} - {self.city}"
