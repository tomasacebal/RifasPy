# API REST de Rifas

API REST simple y funcional para administrar rifas con Flask y SQLite.

## Requisitos
- Python 3.10 o superior
- pip

## Instalacion
```bash
python -m venv .venv
.venv\Scripts\activate
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
    "timestamp": "2026-04-14T18:25:43Z"
  }
}
```

### Error
```json
{
  "success": false,
  "error": {
    "message": "Rifa no encontrada."
  }
}
```

## Ejemplos con curl

### Healthcheck
```bash
curl -X GET http://localhost:6969/api/v1/health
```

### Crear una rifa
```bash
curl -X POST http://localhost:6969/api/v1/rifas ^
  -H "Content-Type: application/json" ^
  -d "{\"numero\": 1, \"nombre\": \"Juan Perez\", \"telefono\": \"1122334455\", \"mail\": \"juan@example.com\"}"
```

Response:

```json
{
  "success": true,
  "data": {
    "numero": 1,
    "nombre": "Juan Perez",
    "telefono": "1122334455",
    "mail": "juan@example.com",
    "timestamp": "2026-04-14T18:25:43Z"
  }
}
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
  -d "{\"nombre\": \"Juan Actualizado\", \"telefono\": \"1199998888\", \"mail\": \"juan.actualizado@example.com\"}"
```

### Actualizar parcialmente una rifa
```bash
curl -X PATCH http://localhost:6969/api/v1/rifas/1 ^
  -H "Content-Type: application/json" ^
  -d "{\"telefono\": \"1100001111\"}"
```

### Eliminar una rifa
```bash
curl -X DELETE http://localhost:6969/api/v1/rifas/1
```

Response:

```json
{
  "success": true,
  "data": {
    "message": "Rifa eliminada correctamente.",
    "numero": 1
  }
}
```

## Ejemplos de errores

### Mail invalido
```bash
curl -X POST http://localhost:6969/api/v1/rifas ^
  -H "Content-Type: application/json" ^
  -d "{\"numero\": 2, \"nombre\": \"Ana\", \"mail\": \"mail-invalido\"}"
```

Response:

```json
{
  "success": false,
  "error": {
    "message": "El campo 'mail' debe tener un formato valido."
  }
}
```

### Numero duplicado
```bash
curl -X POST http://localhost:6969/api/v1/rifas ^
  -H "Content-Type: application/json" ^
  -d "{\"numero\": 1, \"nombre\": \"Otra Persona\"}"
```

Response:

```json
{
  "success": false,
  "error": {
    "message": "Ya existe una rifa con ese numero."
  }
}
```

## Pruebas
```bash
python -m unittest discover -s tests -v
```
