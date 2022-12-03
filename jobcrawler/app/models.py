from django.db import models


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Company(BaseModel):
    title = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    size = models.IntegerField(default=1)
    category = models.IntegerField(default=1)
    description = models.CharField(max_length=255, default='description')

    def __str__(self):
        return self.name


class Job(BaseModel):
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    company = models.ForeignKey(to=Company, on_delete=models.CASCADE)
    salary = models.CharField(max_length=255)
    publish_time = models.CharField(max_length=255)
    link = models.URLField(max_length=255, )

    code = models.CharField(max_length=255)

    class Meta:
        unique_together = ['code', 'company']

    @property
    def short_link(self):
        return self.link[:70]

    def __str__(self):
        return self.title


class Skill(BaseModel):
    name = models.CharField(max_length=255)


class JobDetail(BaseModel):
    job = models.OneToOneField(to=Job, on_delete=models.CASCADE)

    category = models.CharField(max_length=255)
    contract_type = models.CharField(max_length=255)
    experience = models.CharField(max_length=255)
    gender = models.IntegerField()
    military = models.IntegerField()
    education_degree = models.IntegerField()

    skills = models.ManyToManyField(to=Skill, blank=True)
