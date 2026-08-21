import sqlite3
from contextlib import contextmanager
from pathlib import Path
import uuid
from shared.config import SQLITE_DB_PATH
from shared.logging_utils import get_logger

logger = get_logger(__name__)


@contextmanager
def get_connection():
    Path(SQLITE_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def create_tables() -> None:
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS parking_spaces (
                space_id TEXT PRIMARY KEY,
                zone TEXT NOT NULL,
                floor INTEGER NOT NULL,
                spot_number TEXT NOT NULL,
                vehicle_type TEXT NOT NULL,
                price_per_hour REAL NOT NULL,
                is_available INTEGER NOT NULL DEFAULT 1,
                last_updated TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                reservation_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                car_number TEXT NOT NULL,
                zone TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL
            )
        """)
    logger.info("parking_spaces and reservations tables ready")


def insert_parking_space(space: dict) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO parking_spaces
                (space_id, zone, floor, spot_number, vehicle_type,
                 price_per_hour, is_available, last_updated)
            VALUES (:space_id, :zone, :floor, :spot_number, :vehicle_type,
                    :price_per_hour, :is_available, :last_updated)
            """,
            space,
        )


def get_available_spaces(zone: str | None = None, vehicle_type: str | None = None) -> list[dict]:
    query = "SELECT * FROM parking_spaces WHERE is_available = 1"
    params: list = []
    if zone:
        query += " AND zone = ?"
        params.append(zone)
    if vehicle_type:
        query += " AND vehicle_type = ?"
        params.append(vehicle_type)

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def get_all_spaces() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM parking_spaces").fetchall()
    return [dict(r) for r in rows]




def insert_reservation(reservation: dict) -> str:
    reservation_id = reservation.get("reservation_id") or uuid.uuid4().hex[:12]
    reservation = {**reservation, "reservation_id": reservation_id}
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO reservations
                (reservation_id, name, surname, car_number, zone,
                 start_time, end_time, status, created_at)
            VALUES (:reservation_id, :name, :surname, :car_number, :zone,
                    :start_time, :end_time, :status, :created_at)
            """,
            reservation,
        )
    return reservation_id


def find_overlapping_reservations(car_number: str, start_time: str, end_time: str) -> list[dict]:
    """Existing non-rejected reservations for this car_number whose period overlaps [start_time, end_time)."""
    query = """
        SELECT * FROM reservations
        WHERE car_number = ?
          AND status != 'rejected'
          AND start_time < ?
          AND end_time > ?
    """
    with get_connection() as conn:
        rows = conn.execute(query, (car_number, end_time, start_time)).fetchall()
    return [dict(r) for r in rows]

def get_all_reservations() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM reservations").fetchall()
    return [dict(r) for r in rows]

def update_reservation_status(reservation_id: str, status: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE reservations SET status = ? WHERE reservation_id = ?",
            (status, reservation_id),
        )


def get_reservations_by_status(status: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM reservations WHERE status = ?", (status,)).fetchall()
    return [dict(r) for r in rows]