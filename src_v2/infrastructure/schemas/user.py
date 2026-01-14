from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import Any, Optional

from src_v2.domain.value_objects import Name, Email, Password, Balance


class UserResponse(BaseModel):
    # Configuración V2: reemplaza orm_mode = True
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    balance: int
    operations_count: int
    is_active: bool

    # Este validador detecta si el dato es un Value Object y extrae el valor
    @field_validator("name", "email", "balance", mode="before")
    @classmethod
    def unwrap_value_objects(cls, v: Any) -> Any:
        # Si v tiene un atributo 'value' (como tus Value Objects), lo extraemos
        if hasattr(v, 'value'):
            return v.value
        return v


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    balance: int = 0


class UserUpdate(BaseModel):
    # Usamos ConfigDict para estandarizar con el resto de la app
    model_config = ConfigDict(from_attributes=True)

    # Recibimos tipos primitivos (opcionales)
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    balance: Optional[int] = None

    # Ya no necesitamos validadores complejos aquí. 
    # La validación de formato la hace Pydantic (como EmailStr).
    # La validación de negocio (reglas de Name, Balance, etc.) 
    # ocurrirá en la capa de aplicación/dominio.