from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from .views import (
    landing,
    register,
    catalogo,
    agregar_al_carrito,
    sumar_al_carrito,
    restar_del_carrito,
    eliminar_del_carrito,
    detalle_carrito,
    limpiar_carrito,
    pasarela_pago,
    procesar_compra,
    DashboardMixinView,
    HistorialPedidosView,
    VistaPermisoMixinView,
    ProductoListView,
    ProductoCreateView,
    ProductoUpdateView,
    ProductoDeleteView,
    DireccionListView,
    DireccionCreateView,
    DireccionUpdateView,
    DireccionDeleteView,
)

urlpatterns = [
    path('', landing, name='home'),

    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("register/", register, name="register"),
    path('dashboard/cambiar-password/',
         auth_views.PasswordChangeView.as_view(
             template_name='cambiar_password.html',
             # Lo devuelve al panel al terminar
             success_url=reverse_lazy('dashboard')
         ),
         name='cambiar_password'),

    path("dashboard/", DashboardMixinView.as_view(), name="dashboard"),
    path("mis-pedidos/", HistorialPedidosView.as_view(), name="mis_pedidos"),

    path("mis-direcciones/", DireccionListView.as_view(), name="direccion_list"),
    path("mis-direcciones/nueva/",
         DireccionCreateView.as_view(), name="direccion_create"),
    path("mis-direcciones/editar/<int:pk>/",
         DireccionUpdateView.as_view(), name="direccion_edit"),
    path("mis-direcciones/eliminar/<int:pk>/",
         DireccionDeleteView.as_view(), name="direccion_delete"),

    path("inventario/", VistaPermisoMixinView.as_view(), name="inventario"),
    path("catalogo/", catalogo, name="catalogo"),

    path('agregar/<int:producto_id>/',
         agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/sumar/<int:producto_id>/',
         sumar_al_carrito, name='sumar_al_carrito'),
    path('carrito/restar/<int:producto_id>/',
         restar_del_carrito, name='restar_del_carrito'),
    path('carrito/eliminar/<int:producto_id>/',
         eliminar_del_carrito, name='eliminar_del_carrito'),

    path('carrito/', detalle_carrito, name='detalle_carrito'),
    path('carrito/limpiar/', limpiar_carrito, name='limpiar_carrito'),
    path('carrito/pago-seguro/', pasarela_pago, name='pasarela_pago'),
    path('carrito/pagar/', procesar_compra, name='procesar_compra'),

    # Rutas CRUD de Productos (Módulo 7)
    path('products/', ProductoListView.as_view(), name='producto_list'),
    path('products/create/', ProductoCreateView.as_view(), name='producto_create'),
    path('products/edit/<int:pk>/',
         ProductoUpdateView.as_view(), name='producto_edit'),
    path('products/delete/<int:pk>/',
         ProductoDeleteView.as_view(), name='producto_delete'),
]
