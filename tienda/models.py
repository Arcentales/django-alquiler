from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField(blank=True, null=True, unique=True)
    telefono = models.CharField(max_length=30, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


class Pelicula(models.Model):
    titulo = models.CharField(max_length=200)
    anio = models.PositiveIntegerField(validators=[MinValueValidator(1900)], verbose_name="Año")
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="peliculas")
    precio_alquiler = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal("0"))])

    class Meta:
        ordering = ["titulo", "anio"]
        unique_together = [("titulo", "anio")]

    def __str__(self) -> str:
        return f"{self.titulo} ({self.anio})"


class Alquiler(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="alquileres")
    pelicula = models.ForeignKey(Pelicula, on_delete=models.PROTECT, related_name="alquileres")

    # Usamos default para que la simulación pueda fijar fechas explícitas.
    fecha_alquiler = models.DateField(default=timezone.localdate)
    fecha_devolucion = models.DateField(blank=True, null=True)
    pagado = models.BooleanField(default=False)

    # Guardamos el precio en el momento del alquiler para que no cambie si cambia la película.
    precio = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ["-fecha_alquiler", "-id"]

    def __str__(self) -> str:
        return f"Alquiler: {self.pelicula} - {self.cliente}"

    def marcar_pagado(self, fecha_devolucion=None) -> None:
        """
        Marca el alquiler como pagado y (opcionalmente) registra la devolución.
        """
        if fecha_devolucion is None:
            fecha_devolucion = timezone.localdate()

        self.pagado = True
        self.fecha_devolucion = fecha_devolucion
        self.save(update_fields=["pagado", "fecha_devolucion"])

    def save(self, *args, **kwargs):
        if self.precio is None:
            self.precio = self.pelicula.precio_alquiler
        super().save(*args, **kwargs)
