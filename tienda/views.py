import datetime
import random

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import AlquilerCreateForm, MarcarPagadoForm, SimularVentasForm
from .models import Alquiler, Categoria, Cliente, Pelicula


def index(request: HttpRequest) -> HttpResponse:
    total_peliculas = Pelicula.objects.count()
    total_clientes = Cliente.objects.count()
    alquileres_pendientes = Alquiler.objects.filter(pagado=False).count()
    ingresos = (
        Alquiler.objects.filter(pagado=True)
        .aggregate(total=Sum("precio"))
        .get("total")
        or 0
    )

    return render(
        request,
        "tienda/index.html",
        {
            "total_peliculas": total_peliculas,
            "total_clientes": total_clientes,
            "alquileres_pendientes": alquileres_pendientes,
            "ingresos": ingresos,
        },
    )


# ── Categorias ────────────────────────────────────────────────────────────────

class CategoriaListView(ListView):
    model = Categoria
    template_name = "tienda/categoria_list.html"
    context_object_name = "categorias"


class CategoriaCreateView(CreateView):
    model = Categoria
    fields = ["nombre", "descripcion"]
    template_name = "tienda/categoria_form.html"
    success_url = reverse_lazy("categoria_list")


class CategoriaUpdateView(UpdateView):
    model = Categoria
    fields = ["nombre", "descripcion"]
    template_name = "tienda/categoria_form.html"
    success_url = reverse_lazy("categoria_list")


class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = "tienda/categoria_confirm_delete.html"
    success_url = reverse_lazy("categoria_list")


# ── Clientes ──────────────────────────────────────────────────────────────────

class ClienteListView(ListView):
    model = Cliente
    template_name = "tienda/cliente_list.html"
    context_object_name = "clientes"


class ClienteCreateView(CreateView):
    model = Cliente
    fields = ["nombre", "email", "telefono"]
    template_name = "tienda/cliente_form.html"
    success_url = reverse_lazy("cliente_list")


class ClienteUpdateView(UpdateView):
    model = Cliente
    fields = ["nombre", "email", "telefono"]
    template_name = "tienda/cliente_form.html"
    success_url = reverse_lazy("cliente_list")


class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = "tienda/cliente_confirm_delete.html"
    success_url = reverse_lazy("cliente_list")


# ── Peliculas ─────────────────────────────────────────────────────────────────

class PeliculaListView(ListView):
    model = Pelicula
    template_name = "tienda/pelicula_list.html"
    context_object_name = "peliculas"


class PeliculaDetailView(DetailView):
    model = Pelicula
    template_name = "tienda/pelicula_detail.html"
    context_object_name = "pelicula"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["alquileres"] = self.object.alquileres.select_related("cliente").order_by("-fecha_alquiler")
        return ctx


class PeliculaCreateView(CreateView):
    model = Pelicula
    fields = ["titulo", "anio", "categoria", "precio_alquiler"]
    template_name = "tienda/pelicula_form.html"
    success_url = reverse_lazy("pelicula_list")


class PeliculaUpdateView(UpdateView):
    model = Pelicula
    fields = ["titulo", "anio", "categoria", "precio_alquiler"]
    template_name = "tienda/pelicula_form.html"
    success_url = reverse_lazy("pelicula_list")


class PeliculaDeleteView(DeleteView):
    model = Pelicula
    template_name = "tienda/pelicula_confirm_delete.html"
    success_url = reverse_lazy("pelicula_list")


# ── Alquileres ────────────────────────────────────────────────────────────────

class AlquilerCreateView(LoginRequiredMixin, CreateView):
    model = Alquiler
    form_class = AlquilerCreateForm
    template_name = "tienda/alquiler_form.html"
    success_url = reverse_lazy("alquiler_list")


class AlquilerListView(ListView):
    model = Alquiler
    template_name = "tienda/alquiler_list.html"
    context_object_name = "alquileres"
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset().select_related("cliente", "pelicula", "pelicula__categoria")
        pagado = self.request.GET.get("pagado")
        if pagado == "1":
            qs = qs.filter(pagado=True)
        elif pagado == "0":
            qs = qs.filter(pagado=False)
        return qs


class MarcarPagadoView(View):
    template_name = "tienda/marcar_pagado.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        alquiler = get_object_or_404(Alquiler, pk=pk)
        form = MarcarPagadoForm()
        return render(request, self.template_name, {"alquiler": alquiler, "form": form})

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        alquiler = get_object_or_404(Alquiler, pk=pk)
        form = MarcarPagadoForm(request.POST)
        if form.is_valid():
            alquiler.marcar_pagado(fecha_devolucion=form.cleaned_data.get("fecha_devolucion"))
            return redirect("alquiler_list")
        return render(request, self.template_name, {"alquiler": alquiler, "form": form})


# ── Ventas ────────────────────────────────────────────────────────────────────

class VentasListView(ListView):
    model = Alquiler
    template_name = "tienda/ventas_list.html"
    context_object_name = "ventas"

    def get_queryset(self):
        return (
            Alquiler.objects.filter(pagado=True)
            .select_related("cliente", "pelicula", "pelicula__categoria")
            .order_by("-fecha_alquiler")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_ingresos"] = self.get_queryset().aggregate(total=Sum("precio")).get("total") or 0
        return ctx


def simular_ventas(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SimularVentasForm(request.POST)
        if form.is_valid():
            numero = form.cleaned_data["numero_ventas"]
            desde = form.cleaned_data["desde"]
            hasta = form.cleaned_data["hasta"]

            clientes = list(Cliente.objects.all())
            peliculas = list(Pelicula.objects.all())

            if not clientes or not peliculas:
                return render(
                    request,
                    "tienda/simular_ventas.html",
                    {"form": form, "error": "Necesitas al menos 1 cliente y 1 película para simular."},
                )

            delta_dias = (hasta - desde).days if hasta >= desde else 0

            for _ in range(numero):
                cliente = random.choice(clientes)
                pelicula = random.choice(peliculas)
                offset = random.randint(0, max(delta_dias, 0))
                fecha_alquiler = desde + datetime.timedelta(days=offset)
                fecha_devolucion = fecha_alquiler + datetime.timedelta(days=random.randint(0, 7))
                Alquiler.objects.create(
                    cliente=cliente,
                    pelicula=pelicula,
                    fecha_alquiler=fecha_alquiler,
                    pagado=True,
                    fecha_devolucion=fecha_devolucion,
                )

            return redirect("ventas_list")
    else:
        form = SimularVentasForm(
            initial={
                "numero_ventas": 10,
                "desde": timezone.localdate(),
                "hasta": timezone.localdate(),
            }
        )

    return render(request, "tienda/simular_ventas.html", {"form": form})