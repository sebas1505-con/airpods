from django.db import models
import urllib.parse


class Producto(models.Model):
    CATEGORIAS = [
        ("airpods",   "AirPods"),
        ("iphone",    "iPhone"),
        ("samsung",   "Samsung"),
        ("accesorio", "Accesorio"),
        ("otro",      "Otro"),
    ]

    nombre      = models.CharField(max_length=120)
    categoria   = models.CharField(max_length=20, choices=CATEGORIAS, default="airpods")
    descripcion = models.TextField(blank=True)
    precio      = models.PositiveIntegerField(help_text="Precio en pesos COP")
    precio_old  = models.PositiveIntegerField(null=True, blank=True, help_text="Precio tachado")
    stock       = models.PositiveIntegerField(default=0)
    imagen      = models.ImageField(upload_to="productos/", null=True, blank=True)
    activo      = models.BooleanField(default=True)
    destacado   = models.BooleanField(default=False, help_text="Mostrar en la landing")
    creado      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-destacado", "-activo", "nombre"]
        verbose_name = "Producto"
        verbose_name_plural = "Productos"

    def __str__(self):
        return f"{self.nombre} — ${self.precio:,}"

    @property
    def disponible(self):
        return self.activo and self.stock > 0


class Cliente(models.Model):
    nombre   = models.CharField(max_length=120)
    email    = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30)
    ciudad   = models.CharField(max_length=80, blank=True, default="Bogotá")
    creado   = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return f"{self.nombre} ({self.telefono})"

    @property
    def total_pedidos(self):
        return self.pedidos.count()


class Pedido(models.Model):
    ESTADOS = [
        ("nuevo",      "🆕 Nuevo"),
        ("contactado", "📞 Contactado"),
        ("enviado",    "🚚 Enviado"),
        ("entregado",  "✅ Entregado"),
        ("cancelado",  "❌ Cancelado"),
    ]

    cliente      = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="pedidos"
    )
    nombre       = models.CharField(max_length=120)
    email        = models.EmailField(blank=True)
    telefono     = models.CharField(max_length=30)
    producto_txt = models.CharField(max_length=200, verbose_name="Producto solicitado")
    mensaje      = models.TextField(blank=True, verbose_name="Mensaje / dirección")
    estado       = models.CharField(max_length=20, choices=ESTADOS, default="nuevo")
    notas_admin  = models.TextField(blank=True, verbose_name="Notas internas")
    creado       = models.DateTimeField(auto_now_add=True)
    actualizado  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"#{self.pk} — {self.nombre} — {self.producto_txt[:40]}"

    def wa_link(self):
        numero = self.telefono.replace(" ", "").replace("+", "").replace("-", "")
        if not numero.startswith("57"):
            numero = "57" + numero
        msg = f"Hola {self.nombre}, te escribimos de Usados Importados sobre tu pedido de {self.producto_txt}."
        return f"https://wa.me/{numero}?text={urllib.parse.quote(msg)}"