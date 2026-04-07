from django.contrib import admin
from .models import OfertaLaboral

@admin.register(OfertaLaboral)
class OfertaLaboralAdmin(admin.ModelAdmin):
    list_display = ('titulo_puesto', 'empresa', 'modalidad', 'estado', 'fecha_expiracion')
    list_filter = ('estado', 'modalidad', 'empresa')
    search_fields = ('titulo_puesto', 'empresa__nombre_empresa')
    actions = ['marcar_como_aprobada', 'marcar_como_expirada']

    @admin.action(description="Marcar como APROBADAS")
    def marcar_como_aprobada(self, request, queryset):
        filas_actualizadas = queryset.update(estado=OfertaLaboral.Estado.APROBADO)
        self.message_user(request, f"{filas_actualizadas} ofertas laborales marcadas como aprobadas.")

    @admin.action(description="Marcar como EXPIRADAS")
    def marcar_como_expirada(self, request, queryset):
        filas_actualizadas = queryset.update(estado=OfertaLaboral.Estado.EXPIRADO)
        self.message_user(request, f"{filas_actualizadas} ofertas laborales marcadas como expiradas.")
