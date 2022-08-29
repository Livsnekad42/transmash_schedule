from django.contrib import admin
from django.contrib import admin

from .models import *

# class EmployeeAdmin(admin.ModelAdmin):
#   list_display = ('id', 'name', 'photo')
## search_fields = ('name',)


admin.site.register(Employee)
admin.site.register(Skill)
admin.site.register(SkillLevel)
admin.site.register(BranchRequirementSKill)
admin.site.register(EmployeeTechSkill)

admin.site.register(Personal)

# Register your models here.

# Register your models here.
def site():
    return None