# tienda/context_processors.py

def total_carrito(request):
    """
    Suma la cantidad de todos los productos en el carrito de la sesión.
    Esta variable estará disponible en TODOS los archivos HTML.
    """
    total_cantidad = 0

    # Revisamos si existe el carrito en la sesión
    if "carrito" in request.session:
        # Sumamos la "cantidad" de cada producto que esté en el diccionario
        for key, value in request.session["carrito"].items():
            total_cantidad += value["cantidad"]

    return {"cantidad_carrito": total_cantidad}
