# Manual y guía de clase — Alquiler de Películas (Django + SQLite)

Este documento es el **manual del proyecto** y al mismo tiempo una **guía para el aula**: explica _qué hace la aplicación_, _cómo se construyó_, _qué conceptos de Django practican_ y _qué tareas les sirven para reforzar_.

---

## 1. Qué es este proyecto (en una frase)

Es una aplicación web hecha con **Django** que permite registrar **categorías de películas**, **películas**, **clientes** y **alquileres**, y ver **ventas** entendidas como _alquileres ya pagados_. La base de datos es **SQLite** (un solo archivo local, ideal para clase).

---

## 2. Objetivos de aprendizaje (qué van a aprender)

Al trabajar con este repositorio, el estudiante debería poder:

1. Explicar el patrón **MVT** de Django (Modelos, Vistas, Plantillas) y cómo encaja una **petición HTTP** en ese flujo.
2. Crear un **proyecto** y una **app**, registrar la app en `INSTALLED_APPS` y enlazar **URLs**.
3. Definir **modelos** con relaciones (`ForeignKey`), generar **migraciones** y aplicarlas (`migrate`).
4. Construir pantallas **CRUD** (crear, listar, editar, borrar) usando vistas genéricas cuando tiene sentido.
5. **Consultar** y **filtrar** datos desde las vistas (por ejemplo, alquileres pagados vs pendientes).
6. Entender **reglas de negocio simples** en código (por ejemplo: “venta” = alquiler con `pagado=True`).
7. Leer y modificar **plantillas** y usar un **filtro personalizado** para formato de moneda.

---

## 3. Prerrequisitos y materiales

### 3.1. Qué deben saber antes

- Uso básico de **terminal** (cambiar de carpeta, ejecutar comandos).
- **Python 3** instalado (en clase conviene acordar una versión mínima; este proyecto se generó con Django 6).
- Nociones de **HTML** (etiquetas, formularios) ayudan mucho al ver las plantillas.

### 3.2. Qué necesitan en la computadora

- Editor de código (por ejemplo VS Code / Cursor).
- Navegador web.
- Opcional: **Git** (si el docente publica el repo en GitHub/GitLab).

---

## 4. Glosario rápido (vocabulario Django)

| Término       | Significado breve                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------------- |
| **Proyecto**  | Carpeta de configuración global (`alquiler_site/`), URLs raíz, `settings.py`.                           |
| **App**       | Módulo reutilizable con modelos/vistas (`tienda/`). Un proyecto puede tener varias apps.                |
| **Modelo**    | Clase Python que representa una **tabla** en la base de datos.                                          |
| **Migración** | Archivo que describe cambios en el esquema de la BD; se aplica con `migrate`.                           |
| **Vista**     | Función o clase que **recibe** la petición HTTP y **devuelve** una respuesta (HTML, redirección, etc.). |
| **Plantilla** | Archivo HTML con sintaxis Django (`{{ }}`, `{% %}`) para mostrar datos.                                 |
| **URLconf**   | Mapeo “ruta del navegador ↔ vista”.                                                                     |
| **ORM**       | Capa que traduce `Modelo.objects.filter(...)` a **SQL** sin escribir SQL a mano.                        |
| **Admin**     | Panel web incluido en Django para gestionar datos (`/admin/`).                                          |

---

## 5. Caso de negocio (reglas que deben entender)

### 5.1. Entidades

- **Categoría**: agrupa películas (por ejemplo: Acción, Comedia).
- **Película**: tiene título, año, categoría y precio de alquiler en **soles** (el valor numérico se guarda en BD; la **presentación** `S/ 3,50` está en plantillas).
- **Cliente**: quien alquila.
- **Alquiler**: relación entre cliente y película en una fecha; tiene `pagado` y un `precio` “congelado” al momento del alquiler.

### 5.2. Qué cuenta como “venta”

En esta versión didáctica:

- **Venta** = un `Alquiler` con `pagado=True`.

Eso simplifica la clase: no hay otra tabla `Venta`; el ingreso se calcula sumando `precio` de alquileres pagados.

---

## 6. Cómo “piensa” Django: MVT y el recorrido de una petición

### 6.1. MVT (Model–View–Template)

1. **Modelo**: define _qué datos existen_ y cómo se guardan.
2. **Vista**: decide _qué consultar_, _qué validar_ y _qué responder_.
3. **Plantilla**: define _cómo se ve_ la respuesta HTML.

### 6.2. Ejemplo mental (una visita a `/peliculas/`)

1. El navegador pide `GET /peliculas/`.
2. Django busca en `alquiler_site/urls.py` y llega a `tienda/urls.py`.
3. Esa ruta llama a una **vista** (aquí, una vista genérica tipo listado).
4. La vista consulta el **modelo** `Pelicula` en la base de datos.
5. Django renderiza la **plantilla** `templates/tienda/pelicula_list.html` con la lista.

Si un estudiante puede contar ese flujo en voz alta, ya entendió la mitad del framework.

---

## 7. Mapa del repositorio (dónde está cada cosa)

```text
django-alquiler/
├── manage.py                 # Punto de entrada: comandos de Django
├── requirements.txt          # Django (y dependencias) con versiones fijadas
├── db.sqlite3                # Base SQLite (aparece tras migrar; no suele subirse a Git)
├── alquiler_site/            # Proyecto Django
│   ├── settings.py           # Configuración (apps instaladas, plantillas, BD…)
│   └── urls.py               # URLs globales (incluye la app tienda)
├── tienda/                   # App del negocio
│   ├── models.py             # Tablas: Categoria, Pelicula, Cliente, Alquiler
│   ├── views.py              # Lógica de pantallas
│   ├── urls.py               # Rutas de la app
│   ├── forms.py              # Formularios (simulación, marcar pagado, etc.)
│   ├── admin.py              # Registro en el panel admin
│   └── templatetags/
│       └── soles.py          # Filtro |soles → muestra S/ 3,50
└── templates/
    ├── base.html             # Layout común (menú, estilos simples)
    └── tienda/               # Pantallas HTML de la app
```

---

## 8. Cómo se creó este proyecto (reproducible, paso a paso)

> Esta sección sirve para que el docente **muestre el origen** del código, o para que un alumno avanzado lo regenere desde cero en otra carpeta.

### 8.1. Entorno y dependencias

```bash
python -m venv .venv
source .venv/bin/activate          # En Windows: .venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
```

### 8.2. Crear el proyecto y la app

```bash
django-admin startproject alquiler_site .
python manage.py startapp tienda
```

### 8.3. Conectar la app

- En `alquiler_site/settings.py`:
    - Agregar `'tienda'` a `INSTALLED_APPS`.
    - Configurar `TEMPLATES['DIRS']` para que encuentre `templates/`.
- En `alquiler_site/urls.py`:
    - Incluir `path('', include('tienda.urls'))`.

### 8.4. Modelos y base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8.5. Crear superusuario (panel admin)

```bash
python manage.py createsuperuser
```

Luego entrar a `http://127.0.0.1:8000/admin/`.

### 8.6. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

Abrir `http://127.0.0.1:8000/`.

---

## 9. Recorrido didáctico por archivos (qué leer primero)

### 9.1. `tienda/models.py` — el “corazón” de los datos

Aquí se definen tablas y relaciones:

- `Pelicula.categoria` apunta a `Categoria` (**muchos a uno**: muchas películas, una categoría).
- `Alquiler.cliente` y `Alquiler.pelicula` conectan cliente y película (**muchos a uno** en ambos casos).

**Pregunta para la clase:** ¿por qué conviene guardar `Alquiler.precio` si ya existe `Peliculas.precio_alquiler`?

**Respuesta esperada:** porque si mañana cambias el precio de la película, los alquileres viejos deberían conservar el precio histórico.

### 9.2. `tienda/views.py` — reglas y pantallas

Aquí ocurre “lo que el servidor hace”:

- Vistas genéricas para CRUD (menos código repetido, ideal para principiantes).
- `MarcarPagadoView` para convertir un pendiente en venta.
- `simular_ventas` para generar datos de práctica.

### 9.3. `tienda/urls.py` — el mapa de la web

Cada `path(...)` es una **entrada del menú** en términos técnicos: une una URL con una vista.

### 9.4. `templates/` — lo que ve el usuario

- `base.html`: menú común (para no repetir HTML en cada página).
- Cada pantalla extiende `base` y muestra tablas/formularios.

### 9.5. `tienda/templatetags/soles.py` — presentación de moneda

En plantillas se usa:

```django
{% load soles %}
{{ importe|soles }}
```

Eso separa **dato** (número en BD) de **formato** (cómo se enseña en pantalla).

---

## 10. Tabla de rutas útiles (para practicar lectura de URLs)

| URL                               | Qué hace                                    |
| --------------------------------- | ------------------------------------------- |
| `/`                               | Inicio con resumen e ingresos               |
| `/categorias/`                    | Lista categorías                            |
| `/categorias/nueva/`              | Crear categoría                             |
| `/peliculas/`                     | Lista películas                             |
| `/peliculas/nueva/`               | Crear película                              |
| `/clientes/`                      | Lista clientes                              |
| `/clientes/nuevo/`                | Crear cliente                               |
| `/alquileres/`                    | Lista alquileres (filtro `?pagado=0` o `1`) |
| `/alquileres/nuevo/`              | Crear alquiler                              |
| `/alquileres/<id>/marcar-pagado/` | Marcar pagado (venta)                       |
| `/ventas/`                        | Lista de ventas + total                     |
| `/ventas/simular/`                | Simular ventas                              |
| `/admin/`                         | Panel administración Django                 |

---

## 11. Uso diario (referencia rápida)

### 11.1. Si ya tienes el código en tu máquina

```bash
cd /ruta/al/django-alquiler
source .venv/bin/activate
python manage.py migrate
python manage.py runserver
```

### 11.2. Si partes solo del `requirements.txt` (sin venv empaquetado)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 11.3. Clonar con Git (cuando exista repositorio remoto)

```bash
git clone <URL_DEL_REPO>
cd <nombre_del_repo>
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 12. Tareas de refuerzo (con entregables claros)

Cada tarea incluye **qué deben lograr** y **qué deben entregar** para que el docente evalúe sin ambigüedad.

### Tarea 1 — Disponibilidad de películas

- **Objetivo:** Agregar a `Pelicula` un campo booleano `disponible` (por defecto `True`).
- **Comportamiento:** En “Nuevo alquiler”, solo deben listarse películas con `disponible=True`.
- **Entregar:**
    - Código (migración incluida).
    - Captura de pantalla del formulario mostrando el filtro (antes/después).
    - 2–3 líneas explicando qué consulta del ORM usaron (o en qué parte del formulario lo filtraron).

### Tarea 2 — Reporte de ventas por categoría

- **Objetivo:** En “Ventas”, permitir elegir una **categoría** y ver:
    - listado filtrado
    - **total** de ingresos de esa categoría
- **Entregar:**
    - Captura con al menos 2 categorías distintas probadas.
    - Explicación: “¿por qué el total cambia al filtrar?”

### Tarea 3 — Simulación con rango de precios

- **Objetivo:** Extender “Simular ventas” para que el usuario ingrese **precio mínimo** y **precio máximo** en soles.
- **Comportamiento:** Cada alquiler simulado debe guardar un `precio` aleatorio dentro del rango (y seguir marcado como pagado).
- **Entregar:**
    - Breve prueba: correr simulación y mostrar en `/ventas/` que los precios caen en el rango.

### Tarea 4 — Exportar ventas a CSV

- **Objetivo:** Agregar una acción (botón o URL) que descargue un archivo `.csv` con columnas:
    - fecha, cliente, película, categoría, precio
- **Entregar:**
    - Archivo CSV de ejemplo generado por la app.
    - Código de la vista (comentario: cómo evitan incluir comas rotas en textos, si aplica).

### Tarea 5 — Validación: no duplicar alquiler el mismo día

- **Objetivo:** Evitar que el mismo `cliente` alquile la misma `pelicula` con la misma `fecha_alquiler`.
- **Comportamiento:** Mostrar error de validación amigable en el formulario.
- **Entregar:**
    - Captura del error.
    - Explicación: ¿validaron en el `ModelForm`, en el `Model.clean()`, o en la vista? ¿por qué?

### Tarea 6 (opcional +1 punto) — Prueba automática mínima

- **Objetivo:** Escribir un test en `tienda/tests.py` que verifique una regla (por ejemplo, que al crear un alquiler se asigne precio).
- **Entregar:** `python manage.py test` pasando en su máquina.

---

## 13. Problemas frecuentes y cómo interpretarlos

| Síntoma                                      | Causa común                                     | Qué hacer                                        |
| -------------------------------------------- | ----------------------------------------------- | ------------------------------------------------ |
| `No module named django`                     | Venv no activado / paquetes no instalados       | Activar venv y `pip install -r requirements.txt` |
| Error al migrar                              | Modelos cambiaron sin migración                 | `makemigrations` y luego `migrate`               |
| `DisallowedHost`                             | Host no permitido                               | Revisar `ALLOWED_HOSTS` en `settings.py`         |
| Pantalla sin estilo “raro”                   | Normal: el proyecto prioriza simpleza didáctica | Esperado en esta versión                         |
| `TemplateSyntaxError: Invalid filter: soles` | Falta `{% load soles %}`                        | Agregar `load` en la plantilla                   |

---

## 14. Notas para el docente (evaluación sugerida)

Rúbrica simple (10 puntos):

- **3 pts — MVT y flujo:** explica petición→URL→vista→plantilla con un ejemplo real del proyecto.
- **3 pts — Modelo + migraciones:** crea campo nuevo con migración coherente.
- **2 pts — Consultas:** filtra/agrega correctamente con ORM.
- **2 pts — Calidad de entrega:** capturas, instrucciones reproducibles, sin “funciona en mi PC” sin pasos.

---

## 15. Licencia y uso educativo

Proyecto pensado para **uso educativo**. Si se publica, conviene aclarar versión de Python/Django y si `db.sqlite3` se ignora en Git (lo habitual).


## Entrega
Alumno: Juan Luis Arcentales Panduro  
Código: 001618058  
Token: VZN97VG43E16  
Rama: alumno/juan-luis-arcentales-panduro-VZN9