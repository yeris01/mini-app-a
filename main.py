from math import isfinite
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

BASE_DIR = Path(__file__).resolve().parent

UNIT_GROUPS = {
    "longitud": {
        "label": "Longitud",
        "symbol": "↔",
        "units": {
            "mm": ("Milímetro", 0.001),
            "cm": ("Centímetro", 0.01),
            "m": ("Metro", 1.0),
            "km": ("Kilómetro", 1000.0),
            "in": ("Pulgada", 0.0254),
            "ft": ("Pie", 0.3048),
            "yd": ("Yarda", 0.9144),
            "mi": ("Milla", 1609.344),
        },
    },
    "masa": {
        "label": "Masa",
        "symbol": "◉",
        "units": {
            "mg": ("Miligramo", 0.001),
            "g": ("Gramo", 1.0),
            "kg": ("Kilogramo", 1000.0),
            "t": ("Tonelada", 1_000_000.0),
            "oz": ("Onza", 28.349523125),
            "lb": ("Libra", 453.59237),
        },
    },
    "temperatura": {
        "label": "Temperatura",
        "symbol": "°",
        "units": {
            "C": ("Celsius", None),
            "F": ("Fahrenheit", None),
            "K": ("Kelvin", None),
        },
    },
    "volumen": {
        "label": "Volumen",
        "symbol": "◫",
        "units": {
            "ml": ("Mililitro", 0.001),
            "l": ("Litro", 1.0),
            "m3": ("Metro cúbico", 1000.0),
            "tsp": ("Cucharadita", 0.00492892159375),
            "tbsp": ("Cucharada", 0.01478676478125),
            "cup": ("Taza", 0.2365882365),
            "gal": ("Galón (EE. UU.)", 3.785411784),
        },
    },
    "superficie": {
        "label": "Superficie",
        "symbol": "▧",
        "units": {
            "cm2": ("Centímetro cuadrado", 0.0001),
            "m2": ("Metro cuadrado", 1.0),
            "km2": ("Kilómetro cuadrado", 1_000_000.0),
            "ha": ("Hectárea", 10_000.0),
            "ft2": ("Pie cuadrado", 0.09290304),
            "ac": ("Acre", 4046.8564224),
        },
    },
    "tiempo": {
        "label": "Tiempo",
        "symbol": "◷",
        "units": {
            "ms": ("Milisegundo", 0.001),
            "s": ("Segundo", 1.0),
            "min": ("Minuto", 60.0),
            "h": ("Hora", 3600.0),
            "d": ("Día", 86400.0),
            "wk": ("Semana", 604800.0),
        },
    },
    "velocidad": {
        "label": "Velocidad",
        "symbol": "↗",
        "units": {
            "m/s": ("Metro por segundo", 1.0),
            "km/h": ("Kilómetro por hora", 1 / 3.6),
            "mph": ("Milla por hora", 0.44704),
            "kn": ("Nudo", 0.5144444444444445),
        },
    },
    "datos": {
        "label": "Datos",
        "symbol": "▤",
        "units": {
            "B": ("Byte", 1.0),
            "KB": ("Kilobyte", 1000.0),
            "MB": ("Megabyte", 1_000_000.0),
            "GB": ("Gigabyte", 1_000_000_000.0),
            "TB": ("Terabyte", 1_000_000_000_000.0),
            "KiB": ("Kibibyte", 1024.0),
            "MiB": ("Mebibyte", 1_048_576.0),
            "GiB": ("Gibibyte", 1_073_741_824.0),
        },
    },
}

app = FastAPI(title="Cambio — Conversor de unidades", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class ConversionRequest(BaseModel):
    category: str
    value: Annotated[float, Field(allow_inf_nan=False)]
    from_unit: str
    to_unit: str

    @field_validator("value")
    @classmethod
    def value_must_be_finite(cls, value: float) -> float:
        if not isfinite(value):
            raise ValueError("El valor debe ser un número finito.")
        return value


def _to_celsius(value: float, unit: str) -> float:
    if unit == "F":
        return (value - 32) * 5 / 9
    if unit == "K":
        return value - 273.15
    return value


def _from_celsius(value: float, unit: str) -> float:
    if unit == "F":
        return value * 9 / 5 + 32
    if unit == "K":
        return value + 273.15
    return value


@app.get("/", include_in_schema=False)
async def home() -> FileResponse:
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.get("/api/units")
async def get_units() -> dict[str, dict[str, object]]:
    return {
        category: {
            "label": group["label"],
            "symbol": group["symbol"],
            "units": [
                {"code": code, "label": details[0]}
                for code, details in group["units"].items()
            ],
        }
        for category, group in UNIT_GROUPS.items()
    }


@app.post("/api/convert")
async def convert(request: ConversionRequest) -> dict[str, object]:
    group = UNIT_GROUPS.get(request.category)
    if group is None:
        raise HTTPException(status_code=422, detail="La categoría no es válida.")

    units = group["units"]
    if request.from_unit not in units or request.to_unit not in units:
        raise HTTPException(
            status_code=422,
            detail="Una o ambas unidades no pertenecen a esta categoría.",
        )

    if request.category == "temperatura":
        result = _from_celsius(_to_celsius(request.value, request.from_unit), request.to_unit)
    else:
        source_factor = units[request.from_unit][1]
        target_factor = units[request.to_unit][1]
        result = request.value * source_factor / target_factor

    if not isfinite(result):
        raise HTTPException(status_code=422, detail="El resultado está fuera de rango.")

    return {
        "value": request.value,
        "result": result,
        "from_unit": request.from_unit,
        "to_unit": request.to_unit,
    }
