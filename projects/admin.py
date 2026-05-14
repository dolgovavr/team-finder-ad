from django.contrib import admin
from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'description', 'owner__email', 'owner__name', 'owner__surname')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'owner', 'github_url', 'status')
        }),
        ('Участники', {
            'fields': ('participants',)
        }),
        ('Даты', {
            'fields': ('created_at',)
        }),
    )


admin.site.register(Project, ProjectAdmin)