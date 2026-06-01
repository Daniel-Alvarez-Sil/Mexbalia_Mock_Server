from django.urls import path

from .views import (
    cliente_detalle_view,
    clientes_view,
    crear_venta_view,
    oauth_simulation_view,
    producto_detalle_view,
    productos_view,
    venta_detalle_view,
    ventas_por_producto_view,
    ventas_view,
)


urlpatterns = [
    path('oAuth-simulation/', oauth_simulation_view, name='oauth_simulation'),
    path('productos/', productos_view, name='productos'),
    path('productos/<int:producto_id>/', producto_detalle_view, name='producto_detalle'),
    path(
        'productos/<int:producto_id>/ventas/',
        ventas_por_producto_view,
        name='ventas_por_producto',
    ),
    path('clientes/', clientes_view, name='clientes'),
    path('clientes/<int:cliente_id>/', cliente_detalle_view, name='cliente_detalle'),
    path('ventas/', ventas_view, name='ventas'),
    path('ventas/<int:venta_id>/', venta_detalle_view, name='venta_detalle'),
    path('ventas/crear/', crear_venta_view, name='crear_venta'),
]
