import pytest
from datetime import datetime, timedelta
from src.utils import generate_short_code, handle_expiration

class TestGenerateShortCode:
    def test_generate_short_code_length(self):
        """
        Проверяем, что функция возвращает строку заданной длины.
        Например, длина короткого кода может быть 6-8 символов.
        """
        code = generate_short_code()
        assert isinstance(code, str)
        assert 5 <= len(code) <= 10, "Длина кода не соответствует ожидаемым границам"

    def test_generate_short_code_randomness(self):
        """
        Проверяем, что при множественном вызове функция действительно генерирует
        разные значения (хотя бы большую часть).
        """
        codes = {generate_short_code() for _ in range(1000)}
        assert len(codes) == 1000, "Короткий код должен быть уникальным"


class TestHandleExpiration:
    @pytest.mark.parametrize(
        "expires_in_minutes",
        [
            30,   # дата истекает через 30 минут => валидно
            -10,  # дата уже прошла => handle_expiration НЕ выбрасывает ошибку
            0     # дата ровно сейчас => тоже не выбрасывает ошибку
        ]
    )
    def test_handle_expiration(self, expires_in_minutes):
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=expires_in_minutes)
        result = handle_expiration(expires_at)
        assert result == expires_at, "handle_expiration должна возвращать исходную дату"
