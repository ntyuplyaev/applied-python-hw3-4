from datetime import datetime
from jose import jwt
from src.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)


class TestSecurityPassword:
    def test_get_password_hash_and_verify(self):
        password = "SuperSecret123"
        hashed = get_password_hash(password)
        assert hashed != password, "Хеш пароля не должен совпадать с исходным паролем"
        assert verify_password(password, hashed), "Пароль должен успешно верифицироваться"
        assert not verify_password("WrongPassword", hashed), "Неверный пароль не должен верифицироваться"


class TestSecurityToken:
    def test_create_access_token(self):
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert decoded["sub"] == data["sub"], "Payload в токене должен содержать правильный sub"
        assert "exp" in decoded, "Токен должен содержать время истечения (exp)"

        exp = decoded["exp"]
        assert exp > datetime.utcnow().timestamp(), "Токен должен иметь время истечения в будущем"
