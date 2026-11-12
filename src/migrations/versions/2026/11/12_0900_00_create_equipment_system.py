"""create equipment booking and maintenance system

Revision ID: 20261112_labgear
Revises: deb6095af334
Create Date: 2026-11-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261112_labgear"
down_revision: Union[str, Sequence[str], None] = "deb6095af334"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "email", existing_type=sa.String(length=100), type_=sa.String(length=255), existing_nullable=False)
    op.add_column(
        "users",
        sa.Column("role", sa.String(length=20), server_default="student", nullable=False),
    )
    op.create_check_constraint(
        "ck_users_role", "users", "role IN ('student', 'technician', 'admin')"
    )

    op.create_table(
        "equipment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inventory_number", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.String(length=150), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="available", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("inventory_number", name="uq_equipment_inventory_number"),
        sa.CheckConstraint(
            "status IN ('available', 'issued', 'maintenance', 'retired')",
            name="ck_equipment_status",
        ),
    )
    op.create_index("ix_equipment_name", "equipment", ["name"])
    op.create_index("ix_equipment_category", "equipment", ["category"])
    op.create_index("ix_equipment_category_status", "equipment", ["category", "status"])

    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("purpose", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("returned_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["approved_by"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint("ends_at > starts_at", name="ck_reservations_period"),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'issued', 'returned', 'cancelled')",
            name="ck_reservations_status",
        ),
    )
    op.create_index(
        "ix_reservations_equipment_period", "reservations", ["equipment_id", "starts_at", "ends_at"]
    )
    op.create_index("ix_reservations_user_status", "reservations", ["user_id", "status"])

    op.create_table(
        "maintenance_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("equipment_id", sa.Integer(), nullable=False),
        sa.Column("reported_by", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="open", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("resolved_by", sa.Integer(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["equipment_id"], ["equipment.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reported_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["resolved_by"], ["users.id"], ondelete="SET NULL"),
        sa.CheckConstraint(
            "status IN ('open', 'in_progress', 'resolved')",
            name="ck_maintenance_status",
        ),
    )
    op.create_index(
        "ix_maintenance_equipment_status", "maintenance_records", ["equipment_id", "status"]
    )


def downgrade() -> None:
    op.drop_index("ix_maintenance_equipment_status", table_name="maintenance_records")
    op.drop_table("maintenance_records")
    op.drop_index("ix_reservations_user_status", table_name="reservations")
    op.drop_index("ix_reservations_equipment_period", table_name="reservations")
    op.drop_table("reservations")
    op.drop_index("ix_equipment_category_status", table_name="equipment")
    op.drop_index("ix_equipment_category", table_name="equipment")
    op.drop_index("ix_equipment_name", table_name="equipment")
    op.drop_table("equipment")
    op.drop_constraint("ck_users_role", "users", type_="check")
    op.drop_column("users", "role")
    op.alter_column("users", "email", existing_type=sa.String(length=255), type_=sa.String(length=100), existing_nullable=False)
