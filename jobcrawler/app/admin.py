from django.contrib import admin
from django.db.transaction import atomic
from django_object_actions import DjangoObjectActions

from .models import Company, Job

# Register your models here.

admin.site.register(Company)


@admin.register(Job)
class JobAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ['id', 'code', 'short_link', ]
    readonly_fields = ['short_link', ]

    actions = ['start_data']
    change_list_template = 'admin/do.html'

    def get_fields(self, request, obj=None):
        fields = super(JobAdmin, self).get_fields(request, obj)
        fields.remove('short_link')
        return fields

    @atomic
    def start_data(self, request, queryset):
        from .scraper import job_inja
        job_inja.send_first_request(title='python')
