from django.db import models

class Conversacion(models.Model):
    numero_telefono = models.CharField(max_length=20, db_index=True)
    mensaje = models.TextField()
    es_usuario = models.BooleanField(default=True)  # True = usuario, False = bot
    fecha_hora = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['fecha_hora']
        indexes = [
            models.Index(fields=['numero_telefono', 'fecha_hora']),
        ]
    
    def __str__(self):
        tipo = "Usuario" if self.es_usuario else "Bot"
        return f"{tipo} ({self.numero_telefono}): {self.mensaje[:50]}..."