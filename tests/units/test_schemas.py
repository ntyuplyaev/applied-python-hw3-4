import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta
from src.schemas import LinkCreate


class TestLinkCreateSchema:
    def test_expires_at_future(self):
        """
        Проверяем, что при валидных данных (expires_at в будущем)
        схема создаётся успешно.
        """
        future_time = datetime.utcnow() + timedelta(days=1)
        link = LinkCreate(
            original_url="https://example.com",
            custom_alias="my_alias",
            expires_at=future_time
        )
        assert link.expires_at == future_time

    def test_expires_at_past(self):
        """
        Проверяем, что при передаче даты в прошлом Pydantic-валидатор (expires_at)
        выбрасывает ошибку.
        """
        past_time = datetime.utcnow() - timedelta(days=1)
        with pytest.raises(ValidationError) as exc_info:
            LinkCreate(
                original_url="https://example.com",
                custom_alias="old_alias",
                expires_at=past_time
            )
        assert "Expiration date must be in the future" in str(exc_info.value)
