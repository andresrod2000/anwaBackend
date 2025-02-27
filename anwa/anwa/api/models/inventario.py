from django.db import models
class Categorias(models.Model):
    idCategoria = models.AutoField(primary_key=True)
    descripcionCat = models.CharField(max_length=255)
    obsCat = models.TextField()

    def __str__(self):
        return self.descripcionCat


class Inventario(models.Model):
    id_producto = models.AutoField(primary_key=True)
    stock_min = models.IntegerField()
    stock_max = models.IntegerField()
    descripcion = models.TextField()
    saldo_ini = models.IntegerField()
    saldo = models.IntegerField()
    nivel_alerta = models.IntegerField()
    entradas = models.IntegerField()
    salidas = models.IntegerField()
    obsProd = models.TextField()
    categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE, related_name='productos')

    def __str__(self):
        return self.descripcion
    

