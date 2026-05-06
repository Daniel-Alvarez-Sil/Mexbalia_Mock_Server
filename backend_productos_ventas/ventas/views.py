from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Cliente, DetalleVenta, Producto, Venta
from .serializers import (
    ClienteSerializer,
    ProductoSerializer,
    VentaCreateSerializer,
    VentaSerializer,
)


@api_view(['GET', 'POST'])
def productos_view(request):
    if request.method == 'GET':
        productos = Producto.objects.all().order_by('id')
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

    serializer = ProductoSerializer(data=request.data)
    if serializer.is_valid():
        producto = serializer.save()
        return Response(
            ProductoSerializer(producto).data,
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def clientes_view(request):
    if request.method == 'GET':
        clientes = Cliente.objects.all().order_by('id')
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    serializer = ClienteSerializer(data=request.data)
    if serializer.is_valid():
        cliente = serializer.save()
        return Response(
            ClienteSerializer(cliente).data,
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def ventas_view(request):
    ventas = Venta.objects.all().order_by('-fecha')
    serializer = VentaSerializer(ventas, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def venta_detalle_view(request, venta_id):
    try:
        venta = Venta.objects.get(id=venta_id)
    except Venta.DoesNotExist:
        return Response(
            {'error': 'Venta no encontrada'},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = VentaSerializer(venta)
    return Response(serializer.data)


@api_view(['POST'])
@transaction.atomic
def crear_venta_view(request):
    serializer = VentaCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    cliente = None

    cliente_id = data.get('cliente_id')
    if cliente_id:
        try:
            cliente = Cliente.objects.get(id=cliente_id)
        except Cliente.DoesNotExist:
            return Response(
                {'error': 'Cliente no encontrado'},
                status=status.HTTP_404_NOT_FOUND,
            )

    venta = Venta.objects.create(cliente=cliente, total=Decimal('0.00'))
    total = Decimal('0.00')

    for item in data['productos']:
        producto_id = item['producto_id']
        cantidad = item['cantidad']

        try:
            producto = Producto.objects.select_for_update().get(id=producto_id)
        except Producto.DoesNotExist:
            transaction.set_rollback(True)
            return Response(
                {'error': f'Producto con id {producto_id} no encontrado'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not producto.activo:
            transaction.set_rollback(True)
            return Response(
                {'error': f'Producto {producto.nombre} no está activo'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if producto.stock < cantidad:
            transaction.set_rollback(True)
            return Response(
                {
                    'error': f'Stock insuficiente para {producto.nombre}',
                    'stock_disponible': producto.stock,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

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
        producto.save()

        total += subtotal

    venta.total = total
    venta.save()

    return Response(
        VentaSerializer(venta).data,
        status=status.HTTP_201_CREATED,
    )
