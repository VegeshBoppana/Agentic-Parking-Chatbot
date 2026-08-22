"""Tool to collect reservation details, check for conflicts using vehicle number, and submit a pending reservation."""
from datetime import datetime, timezone

from dateutil import parser as date_parser
from langchain.tools import tool

from stage1_rag_chatbot.db.sql_store import find_overlapping_reservations, insert_reservation
from shared.logging_utils import get_logger


logger = get_logger(__name__)


def _to_iso(value: str) -> str:
    """Parses almost any date/time format into a canonical ISO 8601 string."""
    return date_parser.parse(value).isoformat()


@tool
def submit_reservation_request(name: str,surname: str,car_number: str,zone: str,start_time: str,end_time: str,) -> str:
    """Submit a parking reservation request once you have collected the customer's
    name, surname, car/vehicle number, preferred zone (A, B, C, or D), and the
    reservation period as start_time and end_time. Dates/times can be in any
    reasonable format (e.g. "2026-08-25 10:00", "Aug 25 2026 10am") - resolve
    any relative references like "tomorrow" to an absolute date yourself first.
    Checks for conflicting bookings on the same vehicle before submitting. The
    request is saved as 'pending' - it still requires administrator approval."""

    try:
        start_iso = _to_iso(start_time)
        end_iso = _to_iso(end_time)
    except (ValueError, OverflowError):
        return (
            f"Could not understand the date/time provided ('{start_time}' / "
            f"'{end_time}'). Please ask the customer to clarify the reservation period."
        )

    if end_iso <= start_iso:
        return "The reservation end time must be after the start time. Please clarify with the customer."

    conflicts = find_overlapping_reservations(car_number, start_iso, end_iso)
    if conflicts:
        conflict = conflicts[0]
        return (
            f"Cannot submit this request - vehicle {car_number} already has a "
            f"{conflict['status']} reservation from {conflict['start_time']} to "
            f"{conflict['end_time']} (Zone {conflict['zone']}). "
            "Please choose a different time or cancel the existing reservation first."
        )

    reservation = {
        "name": name,
        "surname": surname,
        "car_number": car_number,
        "zone": zone,
        "start_time": start_iso,
        "end_time": end_iso,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    reservation_id = insert_reservation(reservation)
    reservation["reservation_id"] = reservation_id

    logger.info(f"Reservation {reservation_id} submitted for car {car_number}")
    return (
        f"Reservation request submitted (ID: {reservation_id}) for {name} {surname}, "
        f"vehicle {car_number}, Zone {zone}, {start_iso} to {end_iso}. "
        "This is now pending administrator approval."
    )