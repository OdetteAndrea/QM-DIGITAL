from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Categoria(models.Model):
    """
    Molde para clasificar los arreglos florales (ej: Romance, Condolencias, Matrimonios).
    """
    nombre = models.CharField(
        max_length=100, unique=True, verbose_name="Nombre de la Categoría")
    descripcion = models.TextField(
        blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Molde principal para cada arreglo floral que se venderá en la tienda.
    """
    nombre = models.CharField(
        max_length=200, verbose_name="Nombre del Arreglo")
    # Relación 1 a Muchos: Una categoría puede tener muchos productos.
    # Si borras la categoría, se borran sus productos (CASCADE).
    categoria = models.ForeignKey(
        Categoria, on_delete=models.CASCADE, related_name='productos')
    descripcion = models.TextField(verbose_name="Descripción detallada")

    # Para precios en CLP (Pesos Chilenos), solemos usar 0 decimales.
    precio = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="Precio",
        validators=[MinValueValidator(1, message="El precio debe ser mayor a 0")]
    )
    stock = models.PositiveIntegerField(
        default=0, verbose_name="Cantidad en Stock")

    # Requiere instalar la librería Pillow: pip install Pillow
    imagen = models.ImageField(
        upload_to='productos/', blank=True, null=True, verbose_name="Imagen referencial")

    # Manejo de Zonas Horarias (TIMESTAMPTZ)
    creado_en = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(
        auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['-creado_en']  # Ordena mostrando los más nuevos primero

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"


class Pedido(models.Model):
    ESTADOS_PAGO = [
        ('PENDIENTE', 'Pendiente'),
        ('PAGADO', 'Pagado'),
        ('FALLIDO', 'Fallido'),
    ]

    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='pedidos', verbose_name="Cliente")
    fecha_pedido = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha del Pedido")
    total = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="Total Pagado")
    direccion_envio = models.TextField(
        verbose_name="Dirección de Envío", blank=True, null=True)
    estado_pago = models.CharField(
        max_length=20, choices=ESTADOS_PAGO, default='PENDIENTE', verbose_name="Estado del Pago")
    transaccion_id = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="ID de Transacción")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido']

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(
        Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(
        Producto, on_delete=models.SET_NULL, null=True, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=0, verbose_name="Precio Unitario")

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"


class Direccion(models.Model):
    usuario = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='direcciones')
    alias = models.CharField(
        max_length=50, verbose_name="Alias (Ej: Casa, Oficina)", default="Casa")
    calle = models.CharField(max_length=200, verbose_name="Calle y Número")
    comuna = models.CharField(max_length=100, verbose_name="Comuna")
    telefono_contacto = models.CharField(
        max_length=20, verbose_name="Teléfono de Contacto")

    class Meta:
        verbose_name = "Dirección"
        verbose_name_plural = "Direcciones"

    def __str__(self):
        return f"{self.alias} - {self.calle}, {self.comuna}"
