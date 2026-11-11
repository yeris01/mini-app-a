# Cambio — Conversor de unidades

Aplicación web de conversión de unidades con interfaz en español y API en FastAPI. Incluye longitud, masa, temperatura, volumen, superficie, tiempo, velocidad y almacenamiento digital.

## Ejecutar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Abre [http://127.0.0.1:8000](http://127.0.0.1:8000). La documentación interactiva de la API está disponible en `/docs`.

## API

- `GET /api/units`: devuelve las categorías y unidades disponibles.
- `POST /api/convert`: convierte un valor entre dos unidades de la misma categoría.

Ejemplo:

```json
{
  "category": "longitud",
  "value": 1,
  "from_unit": "km",
  "to_unit": "mi"
}
```

La respuesta contiene el valor original, el resultado y los códigos de las unidades. Las conversiones de almacenamiento usan unidades decimales (KB = 1000 B) y binarias (KiB = 1024 B) de forma explícita.

## Pruebas

```powershell
python -m pytest
```
