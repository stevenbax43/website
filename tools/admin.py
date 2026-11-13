from django.contrib import admin
from django.db.models import Count, Q
from .models import (
    ConceptSfbLink,
    InstallatieConcept,
    ProjectMollier,
    SfbClass,
    ToolUsageEvent,
    adress,
)

#this is the way we tell Django to register something on the admin site. 
admin.site.register(adress)
admin.site.register(ProjectMollier)


@admin.register(ToolUsageEvent)
class ToolUsageEventAdmin(admin.ModelAdmin):
    change_list_template = "admin/tools/toolusageevent/change_list.html"
    date_hierarchy = "created_at"
    list_display = ("created_at", "user", "tool", "action")
    list_filter = ("tool", "action", "created_at")
    search_fields = ("user__username", "user__email")
    ordering = ("-created_at",)
    list_per_page = 50

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["usage_summary"] = (
            ToolUsageEvent.objects.values("tool")
            .annotate(
                page_views=Count("id", filter=Q(action="page_view")),
                calculations=Count("id", filter=Q(action="calculation")),
                total=Count("id"),
            )
            .order_by("-total", "tool")
        )
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


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