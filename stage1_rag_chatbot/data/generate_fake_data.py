import random
from datetime import datetime, timedelta

from faker import Faker

from stage1_rag_chatbot.db.sql_store import create_tables, insert_parking_space
from shared.logging_utils import get_logger

logger = get_logger(__name__)
fake = Faker()

ZONES = ["A", "B", "C", "D"]
FLOORS = [1, 2, 3, 4, 5]
VEHICLE_TYPES = ["Car", "Motorcycle", "EV", "Disabled"]

BASE_PRICE_PER_HOUR = {
    "Car": 40.0,
    "Motorcycle": 20.0,
    "EV": 60.0,       # EV charging spots cost more
    "Disabled": 30.0,
}


def _make_space(index: int) -> dict:
    zone = random.choice(ZONES)
    floor = random.choice(FLOORS)
    vehicle_type = random.choices(VEHICLE_TYPES, weights=[60, 15, 15, 10])[0]

    space_id = f"{zone}{floor}-{index:04d}"
    spot_number = f"{zone}{floor}-{random.randint(1, 50):03d}"

    price = BASE_PRICE_PER_HOUR[vehicle_type] * random.uniform(0.9, 1.2)
    is_available = random.random() < 0.7  # ~70% available at any given time

    last_updated = (datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat()

    return {
        "space_id": space_id,
        "zone": zone,
        "floor": floor,
        "spot_number": spot_number,
        "vehicle_type": vehicle_type,
        "price_per_hour": round(price, 2),
        "is_available": int(is_available),
        "last_updated": last_updated,
    }


def generate_fake_spaces(n: int = 200) -> None:
    create_tables()
    for i in range(n):
        insert_parking_space(_make_space(i))
    logger.info(f"Inserted {n} fake parking spaces")


if __name__ == "__main__":
    generate_fake_spaces()