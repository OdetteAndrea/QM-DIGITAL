from django.contrib import admin
from .models import Categoria, Producto, Pedido, DetallePedido

# 1. Redecorando la oficina del gerente (Personalización global del Admin)
admin.site.site_header = "Panel de Control | Boutique Floral Odette"
admin.site.site_title = "Admin Odette"
admin.site.index_title = "Gestión de la Tienda"

# 2. Organizando el archivador de Categorías


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Define cómo se visualiza y gestiona el modelo Categoria en el panel.
    """
    list_display = ('id', 'nombre')  # Columnas visibles en la lista
    search_fields = ('nombre',)     # Barra de búsqueda por nombre
    ordering = ('nombre',)          # Orden alfabético por defecto

# 3. Organizando el archivador de Productos (Arreglos Florales)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """
    Define un panel de administración avanzado para las flores, 
    con filtros, búsquedas y columnas específicas.
    """
    # Columnas que verás al entrar a la lista de productos
    list_display = ('id', 'nombre', 'categoria',
                    'precio', 'stock', 'estado_stock')

    # Filtros laterales para encontrar productos rápidamente
    list_filter = ('categoria', 'creado_en')

    # Barra de búsqueda (busca por nombre del producto o nombre de la categoría)
    search_fields = ('nombre', 'categoria__nombre')

    # Campos de solo lectura (no se pueden editar manualmente)
    readonly_fields = ('creado_en', 'actualizado_en')

    # Agrupación visual de los campos al crear/editar un producto
    fieldsets = (
        ('Información Principal', {
            'fields': ('nombre', 'categoria', 'descripcion', 'imagen')
        }),
        ('Inventario y Precios', {
            'fields': ('precio', 'stock')
        }),
        ('Trazabilidad', {
            'fields': ('creado_en', 'actualizado_en'),
            # Oculta esta sección por defecto para no saturar
            'classes': ('collapse',)
        }),
    )

    # Un pequeño método personalizado para mostrar visualmente si hay poco stock
    @admin.display(description='Estado')
    def estado_stock(self, obj):
        if obj.stock == 0:
            return "❌ Agotado"
        elif obj.stock < 5:
            return "⚠️ Bajo"
        return "✅ Disponible"

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario')
    can_delete = False

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_pedido', 'total')
    list_filter = ('fecha_pedido',)
    inlines = [DetallePedidoInline]
