from django.db import models

class Producto_Categoria(models.Model):
    nombre = models.CharField(max_length=100)  # Nombre de la categoría (ej. Entrantes, Platos principales)
    descripcion = models.TextField(null=True, blank=True)  # Descripción opcional de la categoría
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=255)  # Nombre del producto (ej. Pizza Margarita)
    descripcion = models.TextField(null=True, blank=True)  # Descripción del producto
    precio = models.DecimalField(max_digits=10, decimal_places=2)  # Precio del producto (ej. 15.99)
    categoria = models.ForeignKey(Producto_Categoria, on_delete=models.SET_NULL, null=True, blank=True)  # Relación con la categoría
    disponible = models.BooleanField(default=True)  # Indica si el producto está disponible
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)  # Imagen opcional del producto
    
    def __str__(self):
        return self.nombre
