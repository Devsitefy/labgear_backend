import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from src.config import settings
from src.database import async_session_maker
from src.models.equipment import EquipmentOrm
from src.models.maintenance import MaintenanceRecordOrm
from src.models.reservation import ReservationOrm
from src.models.user import UserOrm
from src.services.security import hash_password


DEMO_USERS = (
    {
        "email": "admin@labgear.com",
        "password": "Admin12345!",
        "role": "admin",
    },
    {
        "email": "technician@labgear.com",
        "password": "Tech12345!",
        "role": "technician",
    },
    {
        "email": "student@labgear.com",
        "password": "Student123!",
        "role": "student",
    },
    {
        "email": "student2@labgear.com",
        "password": "Student123!",
        "role": "student",
    },
)

DEMO_EQUIPMENT = (
    {
        "inventory_number": "LAB-001",
        "name": "Осциллограф Rigol DS1054Z",
        "category": "Измерительное оборудование",
        "description": "Цифровой осциллограф для исследования электрических сигналов",
        "location": "Лаборатория 204",
        "status": "available",
    },
    {
        "inventory_number": "LAB-002",
        "name": "Мультиметр UNI-T UT61E",
        "category": "Измерительное оборудование",
        "description": "Цифровой мультиметр для измерения напряжения, тока и сопротивления",
        "location": "Лаборатория 204",
        "status": "available",
    },
    {
        "inventory_number": "LAB-003",
        "name": "Генератор сигналов FY6900",
        "category": "Генераторы сигналов",
        "description": "Двухканальный генератор сигналов произвольной формы",
        "location": "Лаборатория 206",
        "status": "available",
    },
    {
        "inventory_number": "LAB-004",
        "name": "Источник питания Korad KA3005P",
        "category": "Источники питания",
        "description": "Лабораторный регулируемый источник питания 0–30 В",
        "location": "Лаборатория 206",
        "status": "issued",
    },
    {
        "inventory_number": "LAB-005",
        "name": "Микроскоп Levenhuk 500T",
        "category": "Оптическое оборудование",
        "description": "Тринокулярный микроскоп для учебных и исследовательских работ",
        "location": "Лаборатория 310",
        "status": "available",
    },
    {
        "inventory_number": "LAB-006",
        "name": "3D-принтер Creality Ender-3 V3",
        "category": "Производственное оборудование",
        "description": "Принтер для изготовления учебных прототипов и деталей",
        "location": "Мастерская 012",
        "status": "maintenance",
    },
    {
        "inventory_number": "LAB-007",
        "name": "Паяльная станция Quick 861DW",
        "category": "Паяльное оборудование",
        "description": "Термовоздушная паяльная станция для монтажа компонентов",
        "location": "Мастерская 012",
        "status": "available",
    },
    {
        "inventory_number": "LAB-008",
        "name": "Тепловизор UNI-T UTi260B",
        "category": "Диагностическое оборудование",
        "description": "Тепловизор для бесконтактной диагностики нагрева узлов",
        "location": "Лаборатория 208",
        "status": "available",
    },
    {
        "inventory_number": "LAB-009",
        "name": "3D-сканер Revopoint POP 3",
        "category": "Сканирующее оборудование",
        "description": "Компактный 3D-сканер для оцифровки физических объектов",
        "location": "Мастерская 014",
        "status": "available",
    },
    {
        "inventory_number": "LAB-010",
        "name": "Лабораторный блок питания OWON",
        "category": "Источники питания",
        "description": "Двухканальный источник питания для практических занятий",
        "location": "Лаборатория 204",
        "status": "available",
    },
)


async def get_or_create_user(session, email: str, password: str, role: str) -> UserOrm:
    user = await session.scalar(select(UserOrm).where(UserOrm.email == email))
    if user is None:
        user = UserOrm(
            email=email,
            hashed_password=hash_password(password),
            role=role,
        )
        session.add(user)
        await session.flush()
    return user


async def seed_demo_data() -> None:
    now = datetime.now(timezone.utc)

    async with async_session_maker() as session:
        # Admin credentials are configurable through .env.
        admin = None
        if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
            admin = await session.scalar(
                select(UserOrm).where(UserOrm.email == settings.ADMIN_EMAIL)
            )
            if admin is None:
                admin = UserOrm(
                    email=settings.ADMIN_EMAIL,
                    hashed_password=hash_password(settings.ADMIN_PASSWORD),
                    role="admin",
                )
                session.add(admin)
                await session.flush()
            else:
                admin.role = "admin"

        demo_users: dict[str, UserOrm] = {}
        for item in DEMO_USERS:
            if admin and item["email"].lower() == admin.email.lower():
                demo_user = admin
            else:
                demo_user = await get_or_create_user(
                    session, item["email"], item["password"], item["role"]
                )
            demo_users[item["role"] + ":" + item["email"]] = demo_user

        technician = demo_users["technician:technician@labgear.com"]
        student = demo_users["student:student@labgear.com"]
        student2 = demo_users["student:student2@labgear.com"]

        equipment_by_inventory: dict[str, EquipmentOrm] = {}
        for item in DEMO_EQUIPMENT:
            equipment = await session.scalar(
                select(EquipmentOrm).where(
                    EquipmentOrm.inventory_number == item["inventory_number"]
                )
            )
            if equipment is None:
                equipment = EquipmentOrm(**item)
                session.add(equipment)
                await session.flush()
            equipment_by_inventory[item["inventory_number"]] = equipment

        # Sample bookings cover the main states visible in the UI.
        demo_reservations = (
            {
                "key": "DEMO:pending-oscilloscope",
                "equipment": "LAB-001",
                "user": student,
                "starts_at": now + timedelta(days=2),
                "ends_at": now + timedelta(days=2, hours=2),
                "status": "pending",
            },
            {
                "key": "DEMO:approved-multimeter",
                "equipment": "LAB-002",
                "user": student2,
                "starts_at": now + timedelta(days=1),
                "ends_at": now + timedelta(days=1, hours=2),
                "status": "approved",
            },
            {
                "key": "DEMO:issued-power-supply",
                "equipment": "LAB-004",
                "user": student,
                "starts_at": now - timedelta(minutes=45),
                "ends_at": now + timedelta(hours=2),
                "status": "issued",
            },
            {
                "key": "DEMO:returned-microscope",
                "equipment": "LAB-005",
                "user": student2,
                "starts_at": now - timedelta(days=5, hours=3),
                "ends_at": now - timedelta(days=5, hours=1),
                "status": "returned",
            },
            {
                "key": "DEMO:rejected-generator",
                "equipment": "LAB-003",
                "user": student,
                "starts_at": now - timedelta(days=3),
                "ends_at": now - timedelta(days=3) + timedelta(hours=2),
                "status": "rejected",
            },
        )

        for item in demo_reservations:
            purpose = item["key"].replace("DEMO:", "Демонстрационная заявка: ")
            existing = await session.scalar(
                select(ReservationOrm).where(ReservationOrm.purpose == purpose)
            )
            if existing is not None:
                continue

            starts_at = item["starts_at"]
            ends_at = item["ends_at"]
            status = item["status"]
            reservation = ReservationOrm(
                equipment_id=equipment_by_inventory[item["equipment"]].id,
                user_id=item["user"].id,
                starts_at=starts_at,
                ends_at=ends_at,
                purpose=purpose,
                status=status,
                approved_by=technician.id if status in ("approved", "issued", "returned") else None,
                approved_at=starts_at - timedelta(minutes=10)
                if status in ("approved", "issued", "returned")
                else None,
                issued_at=starts_at if status in ("issued", "returned") else None,
                returned_at=ends_at if status == "returned" else None,
            )
            session.add(reservation)

            if status == "issued":
                equipment_by_inventory[item["equipment"]].status = "issued"

        # An open maintenance ticket demonstrates the repair workflow.
        printer = equipment_by_inventory["LAB-006"]
        maintenance_description = "DEMO: Требуется калибровка оси X после перемещения принтера."
        existing_issue = await session.scalar(
            select(MaintenanceRecordOrm).where(
                MaintenanceRecordOrm.description == maintenance_description
            )
        )
        if existing_issue is None:
            session.add(
                MaintenanceRecordOrm(
                    equipment_id=printer.id,
                    reported_by=student2.id,
                    description=maintenance_description,
                    status="open",
                )
            )
            if printer.status != "retired":
                printer.status = "maintenance"

        await session.commit()

    print("LabGear demo data is ready.")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
