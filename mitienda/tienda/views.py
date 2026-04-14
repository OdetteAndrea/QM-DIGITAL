import uuid
from .carrito import Carrito  # Importamos nuestra nueva clase
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from .models import Producto, Pedido, DetallePedido, Direccion
from .forms import ProductoForm, DireccionForm


def landing(request):
    return render(request, "landing.html")


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "register.html", {"form": form})


class DashboardMixinView(LoginRequiredMixin, TemplateView):
    template_name = "tienda/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Extraemos los últimos 5 pedidos del usuario logueado
        context['pedidos'] = Pedido.objects.filter(
            usuario=self.request.user).order_by('-fecha_pedido')[:5]
        return context


class HistorialPedidosView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'tienda/historial_pedidos.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        return Pedido.objects.filter(usuario=self.request.user).order_by('-fecha_pedido')


class VistaPermisoMixinView(PermissionRequiredMixin, TemplateView):
    permission_required = "auth.view_user"
    template_name = "tienda/inventario.html"


def get_carrito_totals(request):
    """Función auxiliar para calcular rápidamente totales para AJAX."""
    carrito_session = request.session.get("carrito", {})
    total_pagar = sum(item["precio"] * item["cantidad"] for item in carrito_session.values())
    cantidad_total = sum(item["cantidad"] for item in carrito_session.values())
    return int(total_pagar), int(cantidad_total)


def catalogo(request):
    """
    Muestra todos los productos disponibles.
    Si hay una búsqueda en el nav, filtra los resultados.
    """
    # 1. Traemos todas las flores que tengan al menos 1 en stock
    productos = Producto.objects.filter(stock__gt=0)

    # 2. Capturamos lo que el usuario escribió en el buscador (el 'name="q"')
    query = request.GET.get('q')

    # 3. Si escribió algo, filtramos los productos
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query) | Q(
                categoria__nombre__icontains=query)
        )

    # 4. Empaquetamos todo y lo mandamos a la plantilla
    context = {
        'productos': productos,
        'query': query  # Mandamos el texto buscado para mostrarlo en pantalla
    }
    return render(request, 'tienda/catalogo.html', context)


def agregar_al_carrito(request, producto_id):
    """
    Toma el producto de los estantes y lo mete en el canasto del usuario actual.
    """
    # 1. Instanciamos el carrito para el usuario que hace la petición
    carrito = Carrito(request)

    # 2. Buscamos el producto en la base de datos
    producto = Producto.objects.get(id=producto_id)

    # Extraer la cantidad si la petición viene del formulario (Modal POST)
    cantidad_a_agregar = 1
    if request.method == 'POST':
        try:
            cantidad_a_agregar = int(request.POST.get('cantidad', 1))
        except ValueError:
            cantidad_a_agregar = 1

    # 3. Verificamos el stock antes de agregarlo al canasto
    id_str = str(producto.id)
    cantidad_actual = carrito.carrito.get(id_str, {}).get("cantidad", 0)

    if cantidad_actual + cantidad_a_agregar > producto.stock:
        messages.error(
            request, f"No hay suficiente stock. Solo quedan {producto.stock} uds. de '{producto.nombre}'.")
    else:
        carrito.agregar(producto, cantidad=cantidad_a_agregar)
        messages.success(
            request, f"¡{cantidad_a_agregar}x '{producto.nombre}' añadido(s) al canasto!")

    # 4. Lo devolvemos al catálogo para que siga comprando
    return redirect(request.META.get('HTTP_REFERER', 'catalogo'))


def sumar_al_carrito(request, producto_id):
    """
    Suma una unidad al producto en el canasto, verificando stock, y redirige al carrito.
    """
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)

    id_str = str(producto.id)
    cantidad_actual = carrito.carrito.get(id_str, {}).get("cantidad", 0)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if cantidad_actual + 1 > producto.stock:
        if is_ajax:
            return JsonResponse({'success': False, 'error': f"No hay suficiente stock para '{producto.nombre}'."})
        messages.error(
            request, f"No hay suficiente stock para añadir más '{producto.nombre}'.")
    else:
        carrito.agregar(producto, cantidad=1)
        if is_ajax:
            item_data = request.session["carrito"][id_str]
            total_pagar, cantidad_total = get_carrito_totals(request)
            return JsonResponse({
                'success': True,
                'cantidad_item': item_data["cantidad"],
                'subtotal_item': int(item_data["precio"] * item_data["cantidad"]),
                'total_carrito': total_pagar,
                'cantidad_total': cantidad_total
            })
        messages.success(
            request, f"Se ha añadido otra unidad de '{producto.nombre}'.")

    return redirect("detalle_carrito")


def restar_del_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.restar(producto)
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        id_str = str(producto.id)
        item_data = request.session.get("carrito", {}).get(id_str)
        total_pagar, cantidad_total = get_carrito_totals(request)
        
        if item_data:
            return JsonResponse({
                'success': True,
                'eliminado': False,
                'cantidad_item': item_data["cantidad"],
                'subtotal_item': int(item_data["precio"] * item_data["cantidad"]),
                'total_carrito': total_pagar,
                'cantidad_total': cantidad_total
            })
        else:
            return JsonResponse({'success': True, 'eliminado': True, 'total_carrito': total_pagar, 'cantidad_total': cantidad_total})

    messages.info(request, f"Se ha restado una unidad de '{producto.nombre}'.")
    return redirect("detalle_carrito")


def eliminar_del_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = Producto.objects.get(id=producto_id)
    carrito.eliminar(producto)
    
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    if is_ajax:
        total_pagar, cantidad_total = get_carrito_totals(request)
        return JsonResponse({'success': True, 'eliminado': True, 'total_carrito': total_pagar, 'cantidad_total': cantidad_total})

    messages.warning(request, f"Se ha eliminado '{producto.nombre}' del canasto.")
    return redirect("detalle_carrito")


def detalle_carrito(request):
    """
    Saca los productos de la sesión (el canasto) y calcula el total a pagar.
    """
    # 1. Buscamos el canasto en la sesión. Si no existe, devolvemos un diccionario vacío {}
    carrito_session = request.session.get("carrito", {})

    # 2. Calculamos el total sumando (precio * cantidad) de cada ítem
    total = sum(item["precio"] * item["cantidad"]
                for item in carrito_session.values())

    # 3. Traemos las direcciones si el usuario está logueado
    direcciones = []
    if request.user.is_authenticated:
        direcciones = Direccion.objects.filter(usuario=request.user)

    # 4. Pasamos los valores del diccionario y el total a la plantilla
    context = {
        'items_carrito': carrito_session.values(),
        'total_pagar': total,
        'direcciones': direcciones
    }

    return render(request, 'tienda/detalle_carrito.html', context)


def limpiar_carrito(request):
    """
    Vuelca el canasto entero y lo deja vacío.
    """
    carrito = Carrito(request)
    carrito.limpiar()  # Llamamos al método que creamos en carrito.py

    messages.info(request, "Tu canasto ha sido vaciado correctamente.")
    # Redirigimos de vuelta a la página del carrito (que ahora se verá vacía)
    return redirect('detalle_carrito')


@login_required
def pasarela_pago(request):
    """
    Intercepta la compra y muestra la interfaz simulada de un banco para el pago.
    """
    if request.method == 'POST':
        direccion_id = request.POST.get('direccion_envio')
        if not direccion_id:
            messages.error(
                request, "Debes seleccionar una dirección de envío.")
            return redirect('detalle_carrito')

        carrito_session = request.session.get("carrito", {})
        if not carrito_session:
            return redirect('catalogo')

        total = sum(item["precio"] * item["cantidad"]
                    for item in carrito_session.values())
        # Enviamos la dirección seleccionada de forma oculta a la pasarela
        return render(request, 'tienda/pasarela_pago.html', {'total_pagar': total, 'direccion_id': direccion_id})

    return redirect('detalle_carrito')


@login_required
def procesar_compra(request):
    """
    Procesa la compra, crea el pedido, descuenta el stock y vacía el carrito.
    """
    if request.method != 'POST':
        messages.error(request, "Método no permitido para procesar compras.")
        return redirect('detalle_carrito')

    carrito_session = request.session.get("carrito", {})
    if not carrito_session:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('catalogo')

    direccion_id = request.POST.get('direccion_envio')
    if not direccion_id:
        messages.error(
            request, "Debes seleccionar una dirección de envío para continuar.")
        return redirect('detalle_carrito')

    total = sum(item["precio"] * item["cantidad"]
                for item in carrito_session.values())

    try:
        direccion = Direccion.objects.get(
            id=direccion_id, usuario=request.user)
        direccion_texto = f"{direccion.alias} - {direccion.calle}, {direccion.comuna} (Tel: {direccion.telefono_contacto})"

        with transaction.atomic():
            # Generamos un ID de transacción bancaria simulada (Ej: TXN-A1B2C3D4)
            tx_id = f"TXN-{uuid.uuid4().hex[:8].upper()}"

            pedido = Pedido.objects.create(
                usuario=request.user, total=total, direccion_envio=direccion_texto,
                estado_pago='PAGADO', transaccion_id=tx_id
            )

            for key, item in carrito_session.items():
                # select_for_update() bloquea la fila temporalmente para evitar que 2 personas compren el último producto al mismo tiempo
                producto = Producto.objects.select_for_update().get(
                    id=item["producto_id"])

                if producto.stock < item["cantidad"]:
                    raise ValueError(
                        f"Stock insuficiente para '{producto.nombre}'. Quedan {producto.stock} disponibles.")

                # Descontar stock
                producto.stock -= item["cantidad"]
                producto.save()

                # Crear detalle
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=item["cantidad"],
                    precio_unitario=item["precio"]
                )

            # Limpiar carrito
            Carrito(request).limpiar()
            messages.success(
                request, f"¡Gracias por tu compra! Tu pedido #{pedido.id} se ha procesado correctamente.")
    except Direccion.DoesNotExist:
        messages.error(request, "La dirección seleccionada no es válida.")
        return redirect('detalle_carrito')
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('detalle_carrito')

    return redirect('dashboard')

# --- VISTAS CRUD PARA EL MÓDULO DE ADMINISTRACIÓN (Módulo 7) ---


# --- VISTAS CRUD PARA DIRECCIONES DEL CLIENTE ---
class DireccionListView(LoginRequiredMixin, ListView):
    model = Direccion
    template_name = 'tienda/direccion_list.html'
    context_object_name = 'direcciones'

    def get_queryset(self):
        return Direccion.objects.filter(usuario=self.request.user)


class DireccionCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Direccion
    form_class = DireccionForm
    template_name = 'tienda/direccion_form.html'
    success_url = reverse_lazy('direccion_list')
    success_message = "Dirección guardada exitosamente."

    def form_valid(self, form):
        form.instance.usuario = self.request.user
        response = super().form_valid(form)
        # Si viene del carrito, lo devuelve al carrito
        if self.request.GET.get('next') == 'checkout':
            return redirect('detalle_carrito')
        return response


class DireccionUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Direccion
    form_class = DireccionForm
    template_name = 'tienda/direccion_form.html'
    success_url = reverse_lazy('direccion_list')
    success_message = "Dirección actualizada."

    def get_queryset(self):
        return Direccion.objects.filter(usuario=self.request.user)


class DireccionDeleteView(LoginRequiredMixin, DeleteView):
    model = Direccion
    template_name = 'tienda/direccion_confirm_delete.html'
    success_url = reverse_lazy('direccion_list')

    def get_queryset(self):
        return Direccion.objects.filter(usuario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Dirección eliminada de tu libreta.")
        return super().form_valid(form)


class ProductoListView(PermissionRequiredMixin, ListView):
    permission_required = 'tienda.view_producto'
    model = Producto
    template_name = 'tienda/producto_list.html'
    context_object_name = 'productos'


class ProductoCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'tienda.add_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'tienda/producto_form.html'
    success_url = reverse_lazy('producto_list')
    success_message = "Producto '%(nombre)s' creado exitosamente."


class ProductoUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'tienda.change_producto'
    model = Producto
    form_class = ProductoForm
    template_name = 'tienda/producto_form.html'
    success_url = reverse_lazy('producto_list')
    success_message = "Producto '%(nombre)s' actualizado exitosamente."


class ProductoDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = 'tienda.delete_producto'
    model = Producto
    template_name = 'tienda/producto_confirm_delete.html'
    success_url = reverse_lazy('producto_list')

    def form_valid(self, form):
        # Extraemos el nombre antes de eliminarlo para incluirlo en el mensaje
        nombre = self.object.nombre
        response = super().form_valid(form)
        messages.success(
            self.request, f"Producto '{nombre}' eliminado exitosamente.")
        return response
