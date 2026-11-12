from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class EquipmentOrm(Base):
    __tablename__ = "equipment"
    __table_args__ = (
        CheckConstraint(
            "status IN ('available', 'issued', 'maintenance', 'retired')",
            name="ck_equipment_status",
        ),
        UniqueConstraint("inventory_number", name="uq_equipment_inventory_number"),
        Index("ix_equipment_category_status", "category", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    inventory_number: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(150), index=True)
    category: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location: Mapped[str] = mapped_column(String(150))
    status: Mapped[str] = mapped_column(String(20), default="available", server_default="available")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
