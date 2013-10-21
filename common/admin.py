from models import Departamento
from django.contrib import admin

class DepartamentoAdmin(admin.ModelAdmin):
    pass

admin.site.register(Departamento, DepartamentoAdmin)
