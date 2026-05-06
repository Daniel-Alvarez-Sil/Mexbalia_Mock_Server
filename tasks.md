# tasks.md — Backend de Productos y Ventas en Django

## Objetivo

Levantar un backend en **Django + Django REST Framework** para administrar:

- Productos
- Clientes
- Ventas
- Detalle de ventas
- Servicios `GET` para consultar información
- Servicios `POST` para registrar información

---

## 1. Crear entorno de trabajo

### 1.1 Crear carpeta del proyecto

```bash
mkdir backend_productos_ventas
cd backend_productos_ventas
```

### 1.2 Crear entorno virtual

```bash
python -m venv venv
```

### 1.3 Activar entorno virtual

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / macOS / WSL

```bash
source venv/bin/activate
```

### 1.4 Instalar dependencias

```bash
pip install django djangorestframework django-cors-headers
```

### 1.5 Guardar dependencias

```bash
pip freeze > requirements.txt
```

---

## 2. Crear proyecto Django

```bash
django-admin startproject config .
```

Estructura esperada:

```txt
backend_productos_ventas/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── manage.py
├── requirements.txt
└── venv/
```

---

## 3. Crear aplicación principal

```bash
python manage.py startapp ventas
```

Estructura esperada:

```txt
ventas/
├── admin.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── urls.py
└── ...
```

> Nota: Los archivos `serializers.py` y `urls.py` se crearán manualmente.

---

## 4. Configurar `settings.py`

Abrir:

```txt
config/settings.py
```

Agregar las apps instaladas:

```python
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'rest_framework',
    'corsheaders',

    # Local apps
    'ventas',
]
```

Agregar middleware de CORS:

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',

    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

Configurar CORS para desarrollo:

```python
CORS_ALLOW_ALL_ORIGINS = True
```

---

## 5. Crear modelos

Editar:

```txt
ventas/models.py
```

```python
from django.db import models


class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ventas'
    )
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"Venta #{self.id}"


class DetalleVenta(models.Model):
    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name='detalles'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name='detalles_venta'
    )
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
```

---

## 6. Crear migraciones y base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 7. Registrar modelos en admin

Editar:

```txt
ventas/admin.py
```

```python
from django.contrib import admin
from .models import Producto, Cliente, Venta, DetalleVenta


admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
```

Crear superusuario:

```bash
python manage.py createsuperuser
```

---

## 8. Crear serializers

Crear archivo:

```txt
ventas/serializers.py
```

```python
from rest_framework import serializers
from .models import Producto, Cliente, Venta, DetalleVenta


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


class DetalleVentaSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = DetalleVenta
        fields = [
            'id',
            'producto',
            'producto_nombre',
            'cantidad',
            'precio_unitario',
            'subtotal',
        ]


class VentaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    detalles = DetalleVentaSerializer(many=True, read_only=True)

    class Meta:
        model = Venta
        fields = [
            'id',
            'cliente',
            'cliente_nombre',
            'fecha',
            'total',
            'detalles',
        ]


class DetalleVentaCreateSerializer(serializers.Serializer):
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)


class VentaCreateSerializer(serializers.Serializer):
    cliente_id = serializers.IntegerField(required=False, allow_null=True)
    productos = DetalleVentaCreateSerializer(many=True)
```

---

## 9. Crear vistas GET y POST

Editar:

```txt
ventas/views.py
```

```python
from decimal import Decimal

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Producto, Cliente, Venta, DetalleVenta
from .serializers import (
    ProductoSerializer,
    ClienteSerializer,
    VentaSerializer,
    VentaCreateSerializer,
)


@api_view(['GET', 'POST'])
def productos_view(request):
    if request.method == 'GET':
        productos = Producto.objects.all().order_by('id')
        serializer = ProductoSerializer(productos, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ProductoSerializer(data=request.data)
        if serializer.is_valid():
            producto = serializer.save()
            return Response(
                ProductoSerializer(producto).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def clientes_view(request):
    if request.method == 'GET':
        clientes = Cliente.objects.all().order_by('id')
        serializer = ClienteSerializer(clientes, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ClienteSerializer(data=request.data)
        if serializer.is_valid():
            cliente = serializer.save()
            return Response(
                ClienteSerializer(cliente).data,
                status=status.HTTP_201_CREATED
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
            status=status.HTTP_404_NOT_FOUND
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
                status=status.HTTP_404_NOT_FOUND
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
                status=status.HTTP_404_NOT_FOUND
            )

        if not producto.activo:
            transaction.set_rollback(True)
            return Response(
                {'error': f'Producto {producto.nombre} no está activo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if producto.stock < cantidad:
            transaction.set_rollback(True)
            return Response(
                {
                    'error': f'Stock insuficiente para {producto.nombre}',
                    'stock_disponible': producto.stock
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        precio_unitario = producto.precio
        subtotal = precio_unitario * cantidad

        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario,
            subtotal=subtotal
        )

        producto.stock -= cantidad
        producto.save()

        total += subtotal

    venta.total = total
    venta.save()

    return Response(
        VentaSerializer(venta).data,
        status=status.HTTP_201_CREATED
    )
```

---

## 10. Crear URLs de la app

Crear archivo:

```txt
ventas/urls.py
```

```python
from django.urls import path
from .views import (
    productos_view,
    clientes_view,
    ventas_view,
    venta_detalle_view,
    crear_venta_view,
)


urlpatterns = [
    path('productos/', productos_view, name='productos'),
    path('clientes/', clientes_view, name='clientes'),
    path('ventas/', ventas_view, name='ventas'),
    path('ventas/<int:venta_id>/', venta_detalle_view, name='venta_detalle'),
    path('ventas/crear/', crear_venta_view, name='crear_venta'),
]
```

---

## 11. Conectar URLs principales

Editar:

```txt
config/urls.py
```

```python
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('ventas.urls')),
]
```

---

## 12. Levantar servidor

```bash
python manage.py runserver
```

Servidor disponible en:

```txt
http://127.0.0.1:8000/
```

---

## 13. Endpoints disponibles

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/productos/` | Lista productos |
| POST | `/api/productos/` | Crea producto |
| GET | `/api/clientes/` | Lista clientes |
| POST | `/api/clientes/` | Crea cliente |
| GET | `/api/ventas/` | Lista ventas |
| GET | `/api/ventas/<id>/` | Consulta detalle de una venta |
| POST | `/api/ventas/crear/` | Registra una venta |

---

## 14. Ejemplos de pruebas con JSON

### 14.1 Crear producto

**POST**

```txt
http://127.0.0.1:8000/api/productos/
```

Body:

```json
{
  "nombre": "Laptop Lenovo",
  "descripcion": "Laptop para oficina",
  "precio": "12500.00",
  "stock": 10,
  "activo": true
}
```

---

### 14.2 Crear cliente

**POST**

```txt
http://127.0.0.1:8000/api/clientes/
```

Body:

```json
{
  "nombre": "Juan Pérez",
  "correo": "juan@example.com",
  "telefono": "5512345678"
}
```

---

### 14.3 Crear venta

**POST**

```txt
http://127.0.0.1:8000/api/ventas/crear/
```

Body:

```json
{
  "cliente_id": 1,
  "productos": [
    {
      "producto_id": 1,
      "cantidad": 2
    }
  ]
}
```

Respuesta esperada:

```json
{
  "id": 1,
  "cliente": 1,
  "cliente_nombre": "Juan Pérez",
  "fecha": "2026-05-05T12:00:00Z",
  "total": "25000.00",
  "detalles": [
    {
      "id": 1,
      "producto": 1,
      "producto_nombre": "Laptop Lenovo",
      "cantidad": 2,
      "precio_unitario": "12500.00",
      "subtotal": "25000.00"
    }
  ]
}
```

---

## 15. Validaciones incluidas

El backend valida:

- Que el producto exista.
- Que el cliente exista, si se envía `cliente_id`.
- Que el producto esté activo.
- Que exista stock suficiente.
- Que la venta se registre dentro de una transacción.
- Que se descuente el stock automáticamente después de vender.
- Que el total de la venta se calcule automáticamente.

---
