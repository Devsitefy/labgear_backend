from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class UserOrm(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('student', 'technician', 'admin')", name="ck_users_role"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(100))
    role: Mapped[str] = mapped_column(String(20), default="student", server_default="student")
