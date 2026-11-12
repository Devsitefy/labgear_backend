"""add database constraints

Revision ID: deb6095af334
Revises: 1dd0b217d82d
Create Date: 2026-10-02 19:19:47.154636
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "deb6095af334"
down_revision: Union[str, Sequence[str], None] = "1dd0b217d82d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =========================================================
    # CHECK CONSTRAINTS
    # =========================================================

    op.create_check_constraint(
        "ck_rooms_price_positive",
        "rooms",
        "price > 0",
    )

    op.create_check_constraint(
        "ck_rooms_quantity_positive",
        "rooms",
        "quantity >= 0",
    )

    op.create_check_constraint(
        "ck_bookings_price_positive",
        "bookings",
        "price > 0",
    )

    op.create_check_constraint(
        "ck_bookings_dates_valid",
        "bookings",
        "date_to > date_from",
    )

    # =========================================================
    # ROOM IMAGES
    # =========================================================

    op.create_unique_constraint(
        "uq_room_image",
        "room_images",
        ["room_id", "image_id"],
    )

    # Удаляем старые FK
    op.drop_constraint(
        "room_images_image_id_fkey",
        "room_images",
        type_="foreignkey",
    )

    op.drop_constraint(
        "room_images_room_id_fkey",
        "room_images",
        type_="foreignkey",
    )

    # Создаём новые FK с ON DELETE CASCADE
    op.create_foreign_key(
        "fk_room_images_image_id",
        "room_images",
        "images",
        ["image_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_room_images_room_id",
        "room_images",
        "rooms",
        ["room_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # =========================================================
    # ROOMS FACILITIES
    # =========================================================

    op.create_unique_constraint(
        "uq_room_facility",
        "rooms_facilities",
        ["room_id", "facility_id"],
    )

    # Удаляем старые FK
    op.drop_constraint(
        "rooms_facilities_facility_id_fkey",
        "rooms_facilities",
        type_="foreignkey",
    )

    op.drop_constraint(
        "rooms_facilities_room_id_fkey",
        "rooms_facilities",
        type_="foreignkey",
    )

    # Создаём новые FK с ON DELETE CASCADE
    op.create_foreign_key(
        "fk_rooms_facilities_room_id",
        "rooms_facilities",
        "rooms",
        ["room_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_foreign_key(
        "fk_rooms_facilities_facility_id",
        "rooms_facilities",
        "facilities",
        ["facility_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    # =========================================================
    # ROOMS FACILITIES
    # =========================================================

    # Удаляем новые FK
    op.drop_constraint(
        "fk_rooms_facilities_facility_id",
        "rooms_facilities",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_rooms_facilities_room_id",
        "rooms_facilities",
        type_="foreignkey",
    )

    # Возвращаем старые FK без CASCADE
    op.create_foreign_key(
        "rooms_facilities_room_id_fkey",
        "rooms_facilities",
        "rooms",
        ["room_id"],
        ["id"],
    )

    op.create_foreign_key(
        "rooms_facilities_facility_id_fkey",
        "rooms_facilities",
        "facilities",
        ["facility_id"],
        ["id"],
    )

    op.drop_constraint(
        "uq_room_facility",
        "rooms_facilities",
        type_="unique",
    )

    # =========================================================
    # ROOM IMAGES
    # =========================================================

    # Удаляем новые FK
    op.drop_constraint(
        "fk_room_images_image_id",
        "room_images",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_room_images_room_id",
        "room_images",
        type_="foreignkey",
    )

    # Возвращаем старые FK без CASCADE
    op.create_foreign_key(
        "room_images_room_id_fkey",
        "room_images",
        "rooms",
        ["room_id"],
        ["id"],
    )

    op.create_foreign_key(
        "room_images_image_id_fkey",
        "room_images",
        "images",
        ["image_id"],
        ["id"],
    )

    op.drop_constraint(
        "uq_room_image",
        "room_images",
        type_="unique",
    )

    # =========================================================
    # CHECK CONSTRAINTS
    # =========================================================

    op.drop_constraint(
        "ck_bookings_dates_valid",
        "bookings",
        type_="check",
    )

    op.drop_constraint(
        "ck_bookings_price_positive",
        "bookings",
        type_="check",
    )

    op.drop_constraint(
        "ck_rooms_quantity_positive",
        "rooms",
        type_="check",
    )

    op.drop_constraint(
        "ck_rooms_price_positive",
        "rooms",
        type_="check",
    )