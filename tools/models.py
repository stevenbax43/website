from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class adress(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    author_id = models.ForeignKey(User, default=None, on_delete=models.SET_NULL, null=True) 
    date = models.DateTimeField(auto_now_add=True)
    pcode = models.CharField(max_length=6)
    hnumber= models.CharField(max_length=6)
    addition=   models.CharField(max_length=4, blank = True) #black is true betekent dat the field is allowed to be blank
    street= models.TextField()
    place=  models.TextField()
    EP_label= models.TextField(max_length=5,default='')
    EP_surface = models.TextField(max_length=5, default='')
    EP_energie= models.TextField(max_length=5, default='')
    EP_PrimEnergie= models.TextField(max_length=5, default='')
    EP_gebouwklasse = models.TextField(max_length=5, default='')
    EP_TO = models.TextField(max_length=5, default='')
    EP_warmte = models.TextField(max_length=5, default='')
    BAG_surface= models.PositiveIntegerField(default='')
    buildyear= models.PositiveIntegerField(default='')
    purpose= models.TextField()
    calendaryear= models.PositiveIntegerField(default='2017')
    elektra= models.PositiveIntegerField(default='0')
    elektra_terug = models.PositiveIntegerField(default='0',blank = True)
    gas= models.PositiveIntegerField(default='0')
    weii = models.TextField(max_length=20)

    #To see all instances, created in the model database, by title rather than obj1, obj2 etc..,
    # To see all instances, created in the model database, by title rather than obj1, obj2 etc..,
    def __str__(self):
        return f"{self.pcode} - {self.hnumber}"

class ProjectMollier(models.Model):
    user           = models.ForeignKey(User, on_delete=models.CASCADE)
    projectname    = models.CharField(max_length=255)
    sessionstorage = models.JSONField()
    created_at     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.id}: {self.projectname} ({self.user.username})"
    

# voor Tool_A5_NLsfB.py: 
# models.py

class Question(models.Model):
    text = models.TextField()
    phase = models.IntegerField()

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE,related_name="choices")
    text = models.CharField(max_length=255)
    value = models.CharField(max_length=50)  # interne key

class Answer(models.Model):
    session_id = models.CharField(max_length=100)
    question = models.ForeignKey(Question, on_delete=models.CASCADE,related_name="answers")
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    motivation = models.TextField(blank=True, null=True)

class InstallatieConcept(models.Model):
    naam = models.CharField(max_length=100, unique=True)
    synoniemen = models.TextField(
        blank=True,
        help_text="Komma-gescheiden zoektermen, bv: brandklep, fire damper"
    )
    toelichting = models.TextField(blank=True)

    def __str__(self):
        return self.naam


class SfbClass(models.Model):

    classificatie = models.CharField(max_length=20)
    taal = models.CharField(max_length=10)
    tabel = models.CharField(max_length=20)

    code = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
    )

    code_tekst = models.CharField(
        max_length=30,
        blank=True
    )

    omschrijving = models.TextField()

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        related_name="children",
        on_delete=models.CASCADE,
        db_index=True,
    )

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} – {self.omschrijving}"


class ConceptSfbLink(models.Model):

    ROLE_CHOICES = [
        ("werktuigbouwkundig", "Werktuigbouwkundig"),
        ("bouwkundig", "Bouwkundig"),
        ("elektrotechnisch", "Elektrotechnisch"),
        ("verlichting", "Verlichting"),
        ("beveiliging", "Beveiliging"),
        ("besturing", "Besturing / signalering"),
        ("beheer", "Beheer / onderhoud"),
    ]

    concept = models.ForeignKey(
        InstallatieConcept,
        on_delete=models.CASCADE,
        related_name="sfb_links"
    )
    sfb = models.ForeignKey(
        SfbClass,
        on_delete=models.CASCADE
    )
    rol = models.CharField(max_length=30, choices=ROLE_CHOICES)
    toelichting = models.TextField(blank=True)
    
    class Meta:
        unique_together = (
            "concept",
            "sfb",
            "rol"
        )

    def __str__(self):
        return f"{self.concept} → {self.sfb.code} ({self.rol})"


class Ontwerppost(models.Model):
    sfb_class = models.ForeignKey(SfbClass, on_delete=models.CASCADE)

    naam = models.CharField(max_length=255)
    categorie = models.CharField(max_length=100)
    eenheid = models.CharField(max_length=20)

    kengetal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="€ per eenheid"
    )

    toelichting = models.TextField(blank=True)
    
    class Meta:
        ordering = ["naam"]

