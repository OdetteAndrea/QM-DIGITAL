from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Producto, Categoria
from .carrito import Carrito


class MockSession(dict):
    """Simula el comportamiento del diccionario request.session de Django."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.modified = False

class MockRequest:
    """Simula una petición HTTP básica con una sesión."""
    def __init__(self):
        self.session = MockSession()


class ProductoModelTest(TestCase):
    """
    Pruebas para el modelo Producto y sus validaciones personalizadas.
    """

    @classmethod
    def setUpTestData(cls):
        # Creamos una categoría que se usará en todas las pruebas de esta clase.
        cls.categoria = Categoria.objects.create(nombre='Test Category')

    def test_precio_no_puede_ser_cero(self):
        """Verifica que un producto con precio 0 o negativo levante un error de validación."""
        producto = Producto(
            nombre="Producto con Precio Cero", categoria=self.categoria,
            descripcion="Test", precio=0, stock=10
        )
        # El método full_clean() ejecuta todas las validaciones del modelo.
        with self.assertRaises(ValidationError):
            producto.full_clean()

    def test_stock_no_puede_ser_negativo(self):
        """Verifica que un producto con stock negativo levante un error de validación."""
        producto = Producto(
            nombre="Producto con Stock Negativo", categoria=self.categoria,
            descripcion="Test", precio=100, stock=-1
        )
        with self.assertRaises(ValidationError):
            producto.full_clean()


class CarritoTest(TestCase):
    """
    Pruebas unitarias para la lógica de la clase Carrito (agregar, restar, eliminar).
    """

    def setUp(self):
        # Preparamos el entorno creando un producto y un carrito "falso"
        self.categoria = Categoria.objects.create(nombre='Flores Test')
        self.producto = Producto.objects.create(
            nombre="Ramo de Prueba", categoria=self.categoria,
            descripcion="Test", precio=5000, stock=10
        )
        self.request = MockRequest()
        self.carrito = Carrito(self.request)

    def test_agregar_producto_nuevo(self):
        """Verifica que un producto se añade correctamente al canasto vacío."""
        self.carrito.agregar(self.producto, cantidad=2)
        producto_id = str(self.producto.id)
        
        self.assertIn(producto_id, self.carrito.carrito)
        self.assertEqual(self.carrito.carrito[producto_id]['cantidad'], 2)
        self.assertEqual(self.carrito.carrito[producto_id]['precio'], 5000.0)

    def test_restar_producto_hasta_eliminar(self):
        """Verifica que al restar la cantidad a 0, el producto se elimina del canasto."""
        self.carrito.agregar(self.producto, cantidad=2)
        self.carrito.restar(self.producto)
        self.assertEqual(self.carrito.carrito[str(self.producto.id)]['cantidad'], 1)
        
        # Si restamos de nuevo, debería borrarse
        self.carrito.restar(self.producto)
        self.assertNotIn(str(self.producto.id), self.carrito.carrito)

    def test_limpiar_carrito(self):
        """Verifica que el método limpiar deja la sesión vacía."""
        self.carrito.agregar(self.producto, cantidad=5)
        self.carrito.limpiar()
        self.assertEqual(len(self.carrito.carrito), 0)
