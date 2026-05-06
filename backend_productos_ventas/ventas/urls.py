from django.urls import path

from .views import (
    clientes_view,
    crear_venta_view,
    productos_view,
    venta_detalle_view,
    ventas_view,
)


urlpatterns = [
    path('productos/', productos_view, name='productos'),
    path('clientes/', clientes_view, name='clientes'),
    path('ventas/', ventas_view, name='ventas'),
    path('ventas/<int:venta_id>/', venta_detalle_view, name='venta_detalle'),
    path('ventas/crear/', crear_venta_view, name='crear_venta'),
]
