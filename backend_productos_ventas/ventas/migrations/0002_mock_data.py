from decimal import Decimal

from django.db import migrations


def create_mock_data(apps, schema_editor):
    Producto = apps.get_model('ventas', 'Producto')
    Cliente = apps.get_model('ventas', 'Cliente')
    Venta = apps.get_model('ventas', 'Venta')
    DetalleVenta = apps.get_model('ventas', 'DetalleVenta')

    productos_data = [
        {
            'nombre': 'Laptop Lenovo ThinkPad',
            'descripcion': 'Laptop para oficina con 16 GB de RAM y SSD de 512 GB',
            'precio': Decimal('12500.00'),
            'stock': 10,
            'activo': True,
        },
        {
            'nombre': 'Monitor Dell 24',
            'descripcion': 'Monitor Full HD de 24 pulgadas',
            'precio': Decimal('3200.00'),
            'stock': 15,
            'activo': True,
        },
        {
            'nombre': 'Teclado Mecanico Logitech',
            'descripcion': 'Teclado mecanico compacto para productividad',
            'precio': Decimal('1450.00'),
            'stock': 20,
            'activo': True,
        },
        {
            'nombre': 'Mouse Inalambrico Microsoft',
            'descripcion': 'Mouse inalambrico ergonomico',
            'precio': Decimal('650.00'),
            'stock': 25,
            'activo': True,
        },
        {
            'nombre': 'Impresora HP LaserJet',
            'descripcion': 'Impresora laser monocromatica para oficina',
            'precio': Decimal('4800.00'),
            'stock': 6,
            'activo': True,
        },
    ]

    productos = {}
    for data in productos_data:
        producto, _ = Producto.objects.get_or_create(
            nombre=data['nombre'],
            defaults=data,
        )
        productos[data['nombre']] = producto

    clientes_data = [
        {
            'nombre': 'Juan Perez',
            'correo': 'juan@example.com',
            'telefono': '5512345678',
        },
        {
            'nombre': 'Maria Gomez',
            'correo': 'maria@example.com',
            'telefono': '5598765432',
        },
        {
            'nombre': 'Carlos Hernandez',
            'correo': 'carlos@example.com',
            'telefono': '5544556677',
        },
    ]

    clientes = {}
    for data in clientes_data:
        cliente, _ = Cliente.objects.get_or_create(
            correo=data['correo'],
            defaults=data,
        )
        clientes[data['nombre']] = cliente

    ventas_data = [
        {
            'cliente': 'Juan Perez',
            'productos': [
                ('Laptop Lenovo ThinkPad', 1),
                ('Mouse Inalambrico Microsoft', 2),
            ],
        },
        {
            'cliente': 'Maria Gomez',
            'productos': [
                ('Monitor Dell 24', 2),
                ('Teclado Mecanico Logitech', 2),
            ],
        },
        {
            'cliente': 'Carlos Hernandez',
            'productos': [
                ('Impresora HP LaserJet', 1),
                ('Monitor Dell 24', 1),
                ('Mouse Inalambrico Microsoft', 1),
            ],
        },
    ]

    for venta_data in ventas_data:
        venta = Venta.objects.create(
            cliente=clientes[venta_data['cliente']],
            total=Decimal('0.00'),
        )
        total = Decimal('0.00')

        for nombre_producto, cantidad in venta_data['productos']:
            producto = productos[nombre_producto]
            precio_unitario = producto.precio
            subtotal = precio_unitario * cantidad

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal,
            )

            producto.stock -= cantidad
            producto.save(update_fields=['stock'])
            total += subtotal

        venta.total = total
        venta.save(update_fields=['total'])


def delete_mock_data(apps, schema_editor):
    Producto = apps.get_model('ventas', 'Producto')
    Cliente = apps.get_model('ventas', 'Cliente')
    Venta = apps.get_model('ventas', 'Venta')

    correos = [
        'juan@example.com',
        'maria@example.com',
        'carlos@example.com',
    ]
    nombres_productos = [
        'Laptop Lenovo ThinkPad',
        'Monitor Dell 24',
        'Teclado Mecanico Logitech',
        'Mouse Inalambrico Microsoft',
        'Impresora HP LaserJet',
    ]

    Venta.objects.filter(cliente__correo__in=correos).delete()
    Cliente.objects.filter(correo__in=correos).delete()
    Producto.objects.filter(nombre__in=nombres_productos).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_mock_data, delete_mock_data),
    ]
