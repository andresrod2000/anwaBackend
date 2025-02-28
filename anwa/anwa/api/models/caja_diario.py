from django.db import models

class CajaDiario(models.Model):
    fecha = models.DateField()  # Fecha del registro
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)  # Monto inicial de la caja
    monto_final = models.DecimalField(max_digits=10, decimal_places=2)  # Monto final de la caja
    total_ventas = models.DecimalField(max_digits=10, decimal_places=2)  # Total de ventas realizadas en el día
    total_ingresos = models.DecimalField(max_digits=10, decimal_places=2)  # Total de otros ingresos en el día (por ejemplo, pagos de clientes)
    total_egresos = models.DecimalField(max_digits=10, decimal_places=2)  # Total de egresos (por ejemplo, pagos a proveedores, gastos operativos)
    diferencia = models.DecimalField(max_digits=10, decimal_places=2)  # Diferencia entre el monto final y los ingresos y egresos
    usuario_responsable = models.CharField(max_length=255)  # Persona o usuario que registró el cierre de caja
    observaciones = models.TextField(null=True, blank=True)  # Observaciones adicionales sobre el día (opcional)

    def __str__(self):
        return f"Caja del día {self.fecha}"
