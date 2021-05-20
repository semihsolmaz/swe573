from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField, SearchVector
# import tsvector_field
# Create your models here.


class RegistrationApplication(models.Model):
    applicationStatuses = (
        ('1', 'New'),
        ('2', 'Approved'),
        ('3', 'Rejected')
    )

    name = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    email = models.EmailField()
    applicationText = models.TextField(max_length=512)
    applicationDate = models.DateTimeField(default=timezone.now)
    applicationStatus = models.CharField(max_length=20, choices=applicationStatuses, default='1')


class UserProfileInfo(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adminStatus = models.BooleanField(default=False)
    # pip install pillow to use this!
    # Optional: pip install pillow --global-option="build_ext" --global-option="--disable-jpeg"
    # profile_pic = models.ImageField(upload_to='basic_app/profile_pics',blank=True)
    registrationApplication = models.ForeignKey(RegistrationApplication, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Journal(models.Model):

    ISSN = models.CharField(max_length=16)
    Title = models.CharField(max_length=256)
    ISOAbbreviation = models.CharField(max_length=256)

    def __str__(self):
        return self.Title


class Author(models.Model):

    LastName = models.CharField(max_length=32)
    ForeName = models.CharField(max_length=32)
    Initials = models.CharField(max_length=8)

    def __str__(self):
        return self.ForeName + ' ' + self.LastName


class Keyword(models.Model):

    KeywordText = models.TextField(max_length=64)

    def __str__(self):
        return self.KeywordText


class Article(models.Model):

    PMID = models.CharField(max_length=16)
    Title = models.CharField(max_length=256)
    Abstract = models.TextField(max_length=5000, null=True)
    PublicationDate = models.DateField(null=True)

    Journal = models.ForeignKey(Journal, on_delete=models.PROTECT, null=True)
    Keywords = models.ManyToManyField(Keyword)
    Authors = models.ManyToManyField(Author)

    # Tokens = ArrayField(
    #     models.CharField(max_length=128),
    #     size=128
    # )

    Tokens = models.TextField(max_length=100000)

    SearchIndex = SearchVectorField(null=True)
        # [
        # tsvector_field.WeightedColumn('PMID', 'A'),
        # # tsvector_field.WeightedColumn('Authors', 'A'),
        # # tsvector_field.WeightedColumn('Keywords', 'A'),
        # tsvector_field.WeightedColumn('Title', 'A'),
        # # tsvector_field.WeightedColumn('Journal', 'C'),
        # # tsvector_field.WeightedColumn('PublicationDate', 'B'),
        # tsvector_field.WeightedColumn('Abstract', 'B'),
        # tsvector_field.WeightedColumn('Tokens', 'D'),
    # ], 'english')

    def createTSvector(self, *args, **kwargs):
        self.SearchIndex = (
                SearchVector('PMID', weight='A')
                + SearchVector('Title', weight='A')
                + SearchVector('Abstract', weight='B')
                + SearchVector('Tokens', weight='C')
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.Title


class Tag(models.Model):
    Label = models.CharField(max_length=64)
    Description = models.TextField(max_length=1024)
    # Maybe an array field for tokens?
    Tokens = models.TextField(max_length=1024)
    SearchIndex = SearchVectorField(null=True)

    def createTSvector(self, *args, **kwargs):
        self.SearchIndex = (
                SearchVector('Label', weight='A')
                + SearchVector('Tokens', weight='B')
                + SearchVector('Description', weight='C')
        )
        super().save(*args, **kwargs)
