from django.contrib import admin

from .models import Cliente, DetalleVenta, Producto, Venta


admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
