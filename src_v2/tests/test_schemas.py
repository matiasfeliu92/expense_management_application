from src_v2.infrastructure.schemas.user import UserCreate, UserResponse

def test_usercreate_structure():
    # Ahora validamos que el Schema acepte y mantenga tipos primitivos
    uc = UserCreate(
        name="Alice", 
        email="alice@example.com", 
        password="password1", 
        balance=5
    )
    assert uc.name == "Alice"  # Ya no usamos .value
    assert uc.email == "alice@example.com"
    assert isinstance(uc.balance, int)

def test_userresponse_serialization():
    # Simulamos datos que vienen de la base de datos o del dominio
    ur = UserResponse(
        id=1, 
        name="Sam", 
        email="sam@example.com", 
        balance=3, 
        operations_count=0, 
        is_active=True
    )
    
    # Usamos model_dump() en lugar de .dict() para Pydantic V2
    data = ur.model_dump()
    
    assert data["name"] == "Sam"
    assert data["email"] == "sam@example.com"
    assert data["balance"] == 3
    # Verificamos que se serializó como un diccionario plano (JSON compatible)
    assert isinstance(data, dict)