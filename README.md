# Backend de Productos y Ventas

Backend en Django y Django REST Framework para administrar productos, clientes, ventas y detalles de venta.

## Requisitos

- Python 3.12 o compatible
- Git
- pip

## Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Mexbalia_Mock_Server
```

## Crear y activar entorno virtual

```bash
cd backend_productos_ventas
python3 -m venv venv
source venv/bin/activate
```

En Windows:

```bash
cd backend_productos_ventas
python -m venv venv
venv\Scripts\activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Crear base de datos

```bash
python manage.py migrate
```

Al ejecutar las migraciones se crea informacion mock inicial:

- 5 productos activos con stock.
- 3 clientes.
- 3 ventas con detalles.
- Descuento automatico del stock usado en las ventas mock.

## Crear superusuario opcional

Este paso solo es necesario si se quiere entrar al panel de administración de Django.

```bash
python manage.py createsuperuser
```

## Ejecutar servidor

```bash
python manage.py runserver
```

Servidor local:

```txt
http://127.0.0.1:8000/
```

Panel de administración:

```txt
http://127.0.0.1:8000/admin/
```

Base de la API:

```txt
http://127.0.0.1:8000/api/
```

## Endpoints disponibles

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/api/productos/` | Lista productos |
| POST | `/api/productos/` | Crea producto |
| GET | `/api/productos/<id>/` | Consulta un producto por id |
| GET | `/api/productos/<id>/ventas/` | Lista ventas que incluyen un producto |
| GET | `/api/clientes/` | Lista clientes |
| POST | `/api/clientes/` | Crea cliente |
| GET | `/api/ventas/` | Lista ventas |
| GET | `/api/ventas/<id>/` | Consulta el detalle de una venta |
| POST | `/api/ventas/crear/` | Registra una venta |

## Consumir APIs con curl

### Listar productos

```bash
curl http://127.0.0.1:8000/api/productos/
```

### Crear producto

```bash
curl -X POST http://127.0.0.1:8000/api/productos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Laptop Lenovo",
    "descripcion": "Laptop para oficina",
    "precio": "12500.00",
    "stock": 10,
    "activo": true
  }'
```

### Consultar producto por id

```bash
curl http://127.0.0.1:8000/api/productos/1/
```

### Listar clientes

```bash
curl http://127.0.0.1:8000/api/clientes/
```

### Crear cliente

```bash
curl -X POST http://127.0.0.1:8000/api/clientes/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan Perez",
    "correo": "juan@example.com",
    "telefono": "5512345678"
  }'
```

### Crear venta

Antes de crear una venta debe existir al menos un producto con stock disponible. El campo `cliente_id` es opcional.

```bash
curl -X POST http://127.0.0.1:8000/api/ventas/crear/ \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "productos": [
      {
        "producto_id": 1,
        "cantidad": 2
      }
    ]
  }'
```

Respuesta esperada:

```json
{
  "id": 1,
  "cliente": 1,
  "cliente_nombre": "Juan Perez",
  "fecha": "2026-05-06T05:25:36.422881Z",
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

### Listar ventas

```bash
curl http://127.0.0.1:8000/api/ventas/
```

### Consultar detalle de una venta

```bash
curl http://127.0.0.1:8000/api/ventas/1/
```

### Listar ventas de un producto

```bash
curl http://127.0.0.1:8000/api/productos/1/ventas/
```

La respuesta contiene todas las ventas donde aparece el producto indicado, incluyendo los detalles de cada venta.

## Consumir APIs con Postman o Insomnia

1. Ejecutar el servidor con `python manage.py runserver`.
2. Crear una nueva petición HTTP.
3. Usar la URL local correspondiente, por ejemplo `http://127.0.0.1:8000/api/productos/`.
4. Para peticiones `POST`, seleccionar `Body`, formato `JSON`, y agregar el encabezado `Content-Type: application/json`.
5. Enviar la petición.

## Validaciones de venta

Al crear una venta, el backend valida:

- Que el cliente exista si se envía `cliente_id`.
- Que cada producto exista.
- Que cada producto esté activo.
- Que exista stock suficiente.
- Que la venta se registre dentro de una transacción.
- Que el stock se descuente automáticamente.
- Que el total y subtotales se calculen automáticamente.

## Informacion mock inicial

La migracion `ventas/migrations/0002_mock_data.py` crea datos de ejemplo despues de crear las tablas principales.

Productos incluidos:

- Laptop Lenovo ThinkPad
- Monitor Dell 24
- Teclado Mecanico Logitech
- Mouse Inalambrico Microsoft
- Impresora HP LaserJet

Clientes incluidos:

- Juan Perez
- Maria Gomez
- Carlos Hernandez

Estos datos permiten consumir los endpoints inmediatamente despues de ejecutar `python manage.py migrate`.

## Estructura principal

```txt
backend_productos_ventas/
├── config/
│   ├── settings.py
│   └── urls.py
├── ventas/
│   ├── admin.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── manage.py
└── requirements.txt
```
