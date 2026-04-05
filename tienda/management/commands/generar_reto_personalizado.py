import json
import os
import random
import string

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Genera un reto personalizado'

    def add_arguments(self, parser):
        parser.add_argument('--alumno', type=str, required=True)
        parser.add_argument('--codigo', type=str, required=True)

    def generar_token(self, length=12):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

    def slugify(self, texto):
        return texto.lower().replace(" ", "-")

    def handle(self, *args, **kwargs):
        alumno = kwargs['alumno']
        codigo = kwargs['codigo']

        token = self.generar_token()
        token4 = token[:4]

        # Parámetros personalizados
        parametros = {
            "impuesto": random.choice([0.18, 0.15, 0.10]),
            "descuento_max": random.choice([5, 10, 15]),
            "moneda": random.choice(["PEN", "USD"]),
            "dias_gracia": random.randint(1, 5)
        }

        slug = self.slugify(alumno)
        rama = f"alumno/{slug}-{token4}"

        data = {
            "alumno": alumno,
            "codigo": codigo,
            "token": token,
            "rama_obligatoria": rama,
            "parametros": parametros
        }

        # Crear carpeta si no existe
        os.makedirs("retos", exist_ok=True)

        filename = f"retos/{slug}-{codigo}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"✔ Archivo generado: {filename}"))
        self.stdout.write(self.style.SUCCESS(f"✔ Token: {token}"))
        self.stdout.write(self.style.SUCCESS(f"✔ Rama: {rama}"))