from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class MaintenanceRecordOrm(Base):
    __tablename__ = "maintenance_records"
    __table_args__ = (
        CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved')",
            name="ck_maintenance_status",
        ),
        Index("ix_maintenance_equipment_status", "equipment_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id", ondelete="RESTRICT"))
    reported_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="open", server_default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
