from django.contrib import admin
from .models import (
    ConceptSfbLink,
    InstallatieConcept,
    ProjectMollier,
    SfbClass,
    adress,
)

#this is the way we tell Django to register something on the admin site. 
admin.site.register(adress)
admin.site.register(ProjectMollier)


@admin.register(SfbClass)
class SfbClassAdmin(admin.ModelAdmin):
    list_display = ("code", "omschrijving")
    search_fields = ("code", "omschrijving")


class ConceptSfbLinkInline(admin.TabularInline):
    model = ConceptSfbLink
    extra = 0
    autocomplete_fields = ("sfb",)


@admin.register(InstallatieConcept)
class InstallatieConceptAdmin(admin.ModelAdmin):
    list_display = ("naam", "synoniemen")
    search_fields = ("naam", "synoniemen")
    inlines = (ConceptSfbLinkInline,)


@admin.register(ConceptSfbLink)
class ConceptSfbLinkAdmin(admin.ModelAdmin):
    list_display = ("concept", "sfb", "rol")
    search_fields = ("concept__naam", "sfb__code", "sfb__omschrijving")
    autocomplete_fields = ("concept", "sfb")