from django.contrib import admin
from .models import OfertaLaboral

@admin.register(OfertaLaboral)
class OfertaLaboralAdmin(admin.ModelAdmin):
    list_display = ('titulo_puesto', 'empresa', 'modalidad', 'estado', 'fecha_expiracion')
    list_filter = ('estado', 'modalidad', 'empresa')
    search_fields = ('titulo_puesto', 'empresa__nombre_empresa')
    actions = ['marcar_como_aprobada', 'marcar_como_expirada', 'clonar_oferta']

    @admin.action(description="Marcar como APROBADAS")
    def marcar_como_aprobada(self, request, queryset):
        filas_actualizadas = queryset.update(estado=OfertaLaboral.Estado.APROBADO)
        self.message_user(request, f"{filas_actualizadas} ofertas laborales marcadas como aprobadas.")

    @admin.action(description="Marcar como EXPIRADAS")
    def marcar_como_expirada(self, request, queryset):
        filas_actualizadas = queryset.update(estado=OfertaLaboral.Estado.EXPIRADO)
        self.message_user(request, f"{filas_actualizadas} ofertas laborales marcadas como expiradas.")

    @admin.action(description="Clonar oferta (como PENDIENTE)")
    def clonar_oferta(self, request, queryset):
        for obj in queryset:
            # Crear copia del objeto
            obj_copia = obj
            obj_copia.pk = None  # Al poner pk en None, Django crea uno nuevo al guardar
            obj_copia.estado = OfertaLaboral.Estado.PENDIENTE
            obj_copia.titulo_puesto = f"[COPIA] {obj.titulo_puesto}"
            obj_copia.fecha_expiracion = None # Forzar revisión
            obj_copia.save()
        self.message_user(request, f"Se han clonado {queryset.count()} ofertas como PENDIENTES.")
