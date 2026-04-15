# API REST de Rifas

<<<<<<< Updated upstream
=======
API REST simple para administrar rifas con Flask y SQLite.

## Caracteristicas
- CRUD completo bajo `/api/v1/rifas`
- Healthcheck en `/api/v1/health`
- Respuestas JSON consistentes para exito y error
- CORS habilitado para requests normales y preflight `OPTIONS`
- Base SQLite autoinicializada con migracion automatica de la columna `pagado`

>>>>>>> Stashed changes
## Requisitos
- Python 3.10 o superior
- pip

## Instalacion
```bash
pip install -r requirements.txt
```

## Ejecucion
```bash
python run.py
```

La API queda disponible en:

```text
http://localhost:6969/api/v1
```

La base SQLite se crea automaticamente en `instance/rifas.db`.
Si la base ya existe, la app agrega la columna `pagado` automaticamente cuando falta.

## Modelo de datos

| Campo | Tipo JSON | Requerido | Descripcion |
| --- | --- | --- | --- |
| `numero` | `integer` | Si en `POST` | Identificador unico de la rifa. Es inmutable en `PUT` y `PATCH`. |
| `nombre` | `string` | Si en `POST` y `PUT` | Nombre del participante. No admite string vacio ni `null`. |
| `telefono` | `string \| null` | No | Telefono opcional. Se normaliza a `null` si llega vacio. |
| `mail` | `string \| null` | No | Mail opcional con validacion de formato basico. |
| `pagado` | `boolean \| null` | No | Estado de pago opcional. Acepta `true`, `false` o `null`. |
| `timestamp` | `string` | Lo genera el server | Fecha UTC en formato ISO 8601 con sufijo `Z`. |

## Endpoints

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| GET | `/api/v1/health` | Healthcheck |
| GET | `/api/v1/rifas` | Lista todas las rifas |
| GET | `/api/v1/rifas/<numero>` | Obtiene una rifa |
| POST | `/api/v1/rifas` | Crea una rifa |
| PUT | `/api/v1/rifas/<numero>` | Reemplaza una rifa |
| PATCH | `/api/v1/rifas/<numero>` | Actualiza parcialmente una rifa |
| DELETE | `/api/v1/rifas/<numero>` | Elimina una rifa |

## Reglas de validacion
- `POST` exige `numero` y `nombre`.
- `PUT` exige `nombre`. `numero` puede enviarse solo si coincide con la URL.
- `PATCH` exige al menos un campo editable: `nombre`, `telefono`, `mail` o `pagado`.
- `mail` debe tener un formato valido.
- `pagado` solo admite `true`, `false` o `null`.
- Los campos `telefono` y `mail` aceptan `string` o `null`.

## Formato de respuestas

### Exito
```json
{
  "success": true,
  "data": {
    "numero": 1,
    "nombre": "Juan Perez",
    "telefono": "1122334455",
    "mail": "juan@example.com",
    "pagado": null,
    "timestamp": "2026-04-15T12:00:00Z"
  }
}
```

### Error
```json
{
  "success": false,
  "error": {
    "message": "El campo 'pagado' debe ser boolean o null."
  }
}
```

## CORS
- `Access-Control-Allow-Origin` refleja el header `Origin` cuando esta presente.
- Si no llega `Origin`, la respuesta usa `*`.
- `Access-Control-Allow-Headers` devuelve los headers pedidos en el preflight o `Content-Type, Authorization` por defecto.
- Los metodos habilitados son `GET, POST, PUT, PATCH, DELETE, OPTIONS`.

## Ejemplos con curl

### Healthcheck
```bash
curl -X GET http://localhost:6969/api/v1/health
```

### Crear una rifa
```bash
curl -X POST http://localhost:6969/api/v1/rifas ^
  -H "Content-Type: application/json" ^
  -d "{\"numero\": 1, \"nombre\": \"Juan Perez\", \"telefono\": \"1122334455\", \"mail\": \"juan@example.com\", \"pagado\": null}"
```

### Listar rifas
```bash
curl -X GET http://localhost:6969/api/v1/rifas
```

### Obtener una rifa
```bash
curl -X GET http://localhost:6969/api/v1/rifas/1
```

### Reemplazar una rifa
```bash
curl -X PUT http://localhost:6969/api/v1/rifas/1 ^
  -H "Content-Type: application/json" ^
  -d "{\"nombre\": \"Juan Actualizado\", \"telefono\": \"1199998888\", \"mail\": \"nuevo@example.com\", \"pagado\": true}"
```

### Actualizar parcialmente una rifa
```bash
curl -X PATCH http://localhost:6969/api/v1/rifas/1 ^
  -H "Content-Type: application/json" ^
  -d "{\"pagado\": false}"
```

### Eliminar una rifa
```bash
curl -X DELETE http://localhost:6969/api/v1/rifas/1
```

## Ejemplos de errores

### Mail invalido
```bash
curl -X POST http://localhost:6969/api/v1/rifas ^
  -H "Content-Type: application/json" ^
  -d "{\"numero\": 2, \"nombre\": \"Ana\", \"mail\": \"mail-invalido\"}"
```

### Pagado invalido
```bash
curl -X POST http://localhost:6969/api/v1/rifas ^
  -H "Content-Type: application/json" ^
  -d "{\"numero\": 3, \"nombre\": \"Ana\", \"pagado\": \"si\"}"
```

### Numero duplicado
```bash
curl -X POST http://localhost:6969/api/v1/rifas ^
  -H "Content-Type: application/json" ^
  -d "{\"numero\": 1, \"nombre\": \"Otra Persona\"}"
```

## Pruebas
```bash
python -m unittest discover -s tests -v
```
