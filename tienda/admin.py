from django.contrib import admin

from .models import Alquiler, Categoria, Cliente, Pelicula


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ["nombre", "descripcion"]
    search_fields = ["nombre"]


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ["nombre", "email", "telefono", "activo"]
    search_fields = ["nombre", "email"]


@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = ["titulo", "anio", "categoria", "precio_alquiler"]
    list_filter = ["categoria", "anio"]
    search_fields = ["titulo"]


@admin.register(Alquiler)
class AlquilerAdmin(admin.ModelAdmin):
    list_display = ["fecha_alquiler", "cliente", "pelicula", "pagado", "precio", "fecha_devolucion"]
    list_filter = ["pagado", "fecha_alquiler", "fecha_devolucion"]
    search_fields = ["cliente__nombre", "pelicula__titulo"]