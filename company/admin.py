from django.contrib import admin

# Register your models here.
from company.models import Company, OrganizationalLegalForm, Branch, Department

admin.site.register(Company)
admin.site.register(OrganizationalLegalForm)
admin.site.register(Branch)
admin.site.register(Department)
