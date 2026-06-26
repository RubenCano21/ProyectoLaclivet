from django.db import models
from django.core.exceptions import ValidationError


class CatalogoExamen(models.Model):
    nombre = models.CharField(max_length=100)
    area = models.CharField(max_length=50, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        verbose_name = 'Catálogo de Examen'
        verbose_name_plural = 'Catálogos de Exámenes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Examen(models.Model):
    nombre_examen = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    catalogo = models.ForeignKey(CatalogoExamen, on_delete=models.CASCADE, related_name='examenes')

    class Meta:
        verbose_name = 'Examen'
        verbose_name_plural = 'Examenes'
        ordering = ['nombre_examen']

    def __str__(self):
        return f"{self.nombre_examen} ({self.catalogo.nombre})"


class TipoDato(models.TextChoices):
    NUMERICO = "NUM", "Numérico"
    TEXTO = "TXT", "Texto libre"
    SELECT = "SEL", "Selección"


class Parametro(models.Model):
    nombre_parametro = models.CharField(max_length=100)
    unidad_medida = models.CharField(max_length=20, blank=True, null=True)
    examen = models.ForeignKey(Examen, on_delete=models.CASCADE, related_name='parametros')

    # --- NUEVO: lo mínimo para poder renderizar el formulario tipo hemograma ---
    grupo = models.CharField(
        max_length=60, blank=True, null=True,
        help_text="Sección visual, ej: 'Eritrograma', 'Leucograma %', 'Leucograma absoluto'"
    )
    tipo_dato = models.CharField(max_length=3, choices=TipoDato.choices, default=TipoDato.NUMERICO)
    opciones = models.JSONField(blank=True, null=True, help_text="Para tipo SELECT: ['-','+','++']")
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Parámetro'
        verbose_name_plural = 'Parámetros'
        ordering = ['orden', 'nombre_parametro']

    def __str__(self):
        return f"{self.nombre_parametro} ({self.examen.nombre_examen})"


class ValorReferencia(models.Model):
    SEXO_CHOICES = [("A", "Ambos"), ("M", "Macho"), ("H", "Hembra")]

    valor_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valor_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    especie = models.CharField(max_length=50, blank=True, null=True)
    # --- NUEVO: opcional, default 'A' no rompe datos existentes ---
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default="A")
    texto_referencia = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="Para parámetros no numéricos, ej '-a +'"
    )
    parametro = models.ForeignKey(Parametro, on_delete=models.CASCADE, related_name='valores_referencia')

    class Meta:
        verbose_name = 'Valor de Referencia'
        verbose_name_plural = 'Valores de Referencia'
        ordering = ['parametro']

    def __str__(self):
        if self.valor_min is not None or self.valor_max is not None:
            return f"{self.parametro.nombre_parametro} [{self.valor_min} - {self.valor_max}] ({self.especie})"
        return f"{self.parametro.nombre_parametro} [{self.texto_referencia}] ({self.especie})"

    def evaluar(self, valor):
        """Devuelve 'BAJO' | 'NORMAL' | 'ALTO' | None si no aplica (texto libre)."""
        if self.valor_min is None and self.valor_max is None:
            return None
        try:
            valor = float(valor)
        except (TypeError, ValueError):
            return None
        if self.valor_min is not None and valor < float(self.valor_min):
            return "BAJO"
        if self.valor_max is not None and valor > float(self.valor_max):
            return "ALTO"
        return "NORMAL"


# ---------------------------------------------------------------------------
# Captura de resultados (tablas nuevas, no existían en tu app catalogo)
# ---------------------------------------------------------------------------

class OrdenTrabajo(models.Model):
    ESTADOS = [
        ("PEND", "Pendiente"),
        ("PROC", "En proceso"),
        ("VALD", "Validado"),
        ("ENTR", "Entregado"),
        ("ANUL", "Anulado"),
    ]
    paciente = models.ForeignKey("paciente.Paciente", on_delete=models.PROTECT, related_name="ordenes")
    veterinario_solicitante = models.CharField(max_length=120, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=4, choices=ESTADOS, default="PEND")
    observaciones_generales = models.TextField(blank=True)

    def __str__(self):
        return f"OT-{self.id} / {self.paciente}"


class OrdenExamen(models.Model):
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="examenes")
    examen = models.ForeignKey(Examen, on_delete=models.PROTECT, related_name="ordenes_examen")
    muestra = models.ForeignKey(
        "muestra.Muestra", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="ordenes_examen"
    )

    realizado_por = models.CharField(max_length=120, blank=True)
    validado_por = models.CharField(max_length=120, blank=True)
    fecha_resultado = models.DateTimeField(null=True, blank=True)

    observaciones = models.TextField(blank=True)
    alteraciones = models.TextField(blank=True)
    diagnostico = models.TextField(blank=True)
    pronostico = models.CharField(max_length=120, blank=True)

    class Meta:
        unique_together = ["orden", "examen"]

    def __str__(self):
        return f"{self.examen.nombre_examen} - OT{self.orden_id}"


class ResultadoParametro(models.Model):
    orden_examen = models.ForeignKey(OrdenExamen, on_delete=models.CASCADE, related_name="resultados")
    parametro = models.ForeignKey(Parametro, on_delete=models.PROTECT, related_name="resultados")
    valor_numerico = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    valor_texto = models.CharField(max_length=150, blank=True)
    interpretacion = models.CharField(max_length=10, blank=True)  # BAJO / NORMAL / ALTO

    class Meta:
        unique_together = ["orden_examen", "parametro"]

    def clean(self):
        if self.parametro.tipo_dato == TipoDato.NUMERICO and self.valor_numerico is None and not self.valor_texto:
            raise ValidationError("Este parámetro requiere valor numérico.")

    def __str__(self):
        return f"{self.parametro.nombre_parametro}: {self.valor_numerico or self.valor_texto}"