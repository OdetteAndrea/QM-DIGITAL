# odette/carrito.py

class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session

        # Buscamos si el cliente ya tiene un canasto (carrito) asignado en su sesión
        carrito = self.session.get("carrito")

        # Si no tiene, le entregamos un canasto vacío (un diccionario vacío)
        if not carrito:
            self.session["carrito"] = {}
            self.carrito = self.session["carrito"]
        else:
            self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        # Usamos el ID del producto como texto para que sea la llave del diccionario
        id = str(producto.id)

        # Si el producto NO está en el canasto, lo agregamos por primera vez
        if id not in self.carrito.keys():
            self.carrito[id] = {
                "producto_id": producto.id,
                "nombre": producto.nombre,
                "precio": float(producto.precio),
                "cantidad": cantidad,
            }
        # Si ya estaba, simplemente sumamos la cantidad
        else:
            self.carrito[id]["cantidad"] += cantidad

        self.guardar_carrito()

    def guardar_carrito(self):
        # Actualizamos la libreta y le decimos a Django que hubo modificaciones
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def restar(self, producto):
        id = str(producto.id)
        if id in self.carrito.keys():
            self.carrito[id]["cantidad"] -= 1
            if self.carrito[id]["cantidad"] <= 0:
                self.eliminar(producto)
            self.guardar_carrito()

    def eliminar(self, producto):
        id = str(producto.id)
        if id in self.carrito.keys():
            del self.carrito[id]
            self.guardar_carrito()

    def limpiar(self):
        # Vaciamos el canasto (útil para cuando finalmente pagan el pedido)
        self.session["carrito"] = {}
        self.carrito = self.session["carrito"]
        self.session.modified = True
