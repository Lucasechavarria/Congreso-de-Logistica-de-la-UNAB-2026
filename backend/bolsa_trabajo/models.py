from django.db import models
from django.utils import timezone
from api.models import Empresa

class OfertaLaboral(models.Model):
    class Modalidad(models.TextChoices):
        REMOTO = 'REMOTO', 'Remoto'
        PRESENCIAL = 'PRESENCIAL', 'Presencial'
        HIBRIDO = 'HIBRIDO', 'Híbrido'

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        APROBADO = 'APROBADO', 'Aprobado'
        EXPIRADO = 'EXPIRADO', 'Expirado'

    empresa = models.ForeignKey(
        Empresa, 
        on_delete=models.CASCADE, 
        related_name='ofertas_laborales',
        verbose_name="Empresa"
    )
    titulo_puesto = models.CharField(max_length=255, verbose_name="Título del puesto")
    descripcion = models.TextField(verbose_name="Descripción")
    requisitos = models.TextField(verbose_name="Requisitos")
    modalidad = models.CharField(
        max_length=20, 
        choices=Modalidad.choices, 
        default=Modalidad.PRESENCIAL,
        verbose_name="Modalidad"
    )
    ubicacion = models.CharField(max_length=255, verbose_name="Ubicación")
    canal_postulacion = models.TextField(verbose_name="Canal de postulación")
    estado = models.CharField(
        max_length=20, 
        choices=Estado.choices, 
        default=Estado.PENDIENTE,
        verbose_name="Estado"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    fecha_expiracion = models.DateTimeField(verbose_name="Fecha de expiración")

    def is_activa(self):
        """
        Una oferta está activa si su estado es APROBADO y la fecha de expiración es mayor a la actual.
        """
        now = timezone.now()
        return self.estado == self.Estado.APROBADO and self.fecha_expiracion > now

    def __str__(self):
        return f"{self.titulo_puesto} - {self.empresa.nombre_empresa}"

    class Meta:
        verbose_name = "Oferta Laboral"
        verbose_name_plural = "Ofertas Laborales"
        ordering = ['-fecha_creacion']
