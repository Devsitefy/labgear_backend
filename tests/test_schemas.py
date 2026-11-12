from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from src.schemas.reservation import ReservationCreate
from src.schemas.equipment import EquipmentCreate


def test_reservation_accepts_valid_timezone_aware_period():
    start = datetime.now(timezone.utc) + timedelta(days=1)
    reservation = ReservationCreate(
        equipment_id=1,
        starts_at=start,
        ends_at=start + timedelta(hours=2),
        purpose="Проведение лабораторной работы",
    )
    assert reservation.ends_at > reservation.starts_at


def test_reservation_rejects_invalid_period():
    start = datetime.now(timezone.utc)
    with pytest.raises(ValidationError):
        ReservationCreate(
            equipment_id=1,
            starts_at=start,
            ends_at=start,
            purpose="Проведение лабораторной работы",
        )


def test_reservation_rejects_naive_datetime():
    start = datetime(2026, 11, 20, 10, 0)
    with pytest.raises(ValidationError):
        ReservationCreate(
            equipment_id=1,
            starts_at=start,
            ends_at=start + timedelta(hours=1),
            purpose="Проведение лабораторной работы",
        )


def test_equipment_inventory_number_is_required():
    with pytest.raises(ValidationError):
        EquipmentCreate(
            inventory_number="",
            name="Осциллограф",
            category="Измерительное оборудование",
            location="Лаборатория 204",
        )
