from langchain.tools import tool

from stage1_rag_chatbot.db.sql_store import get_reservation_by_id, get_reservations_by_car_number


def _format(r: dict) -> str:
    return (
        f"Reservation {r['reservation_id']} - Status: {r['status']}\n"
        f"{r['name']} {r['surname']}, vehicle {r['car_number']}, Zone {r['zone']}, "
        f"{r['start_time']} to {r['end_time']}"
    )


@tool
def check_reservation_status(reservation_id: str = "", car_number: str = "") -> str:
    """Check the current status of an existing reservation (pending, awaiting_approval,
    approved, or rejected). Use reservation_id if the customer gave it (it was shown
    to them at submission time), otherwise use car_number to look up by vehicle."""
    if reservation_id:
        reservation = get_reservation_by_id(reservation_id)
        if not reservation:
            return f"No reservation found with ID {reservation_id}."
        return _format(reservation)

    if car_number:
        reservations = get_reservations_by_car_number(car_number)
        if not reservations:
            return f"No reservations found for vehicle {car_number}."
        return "\n\n".join(_format(r) for r in reservations)

    return "Please provide either the reservation ID or the vehicle/car number to check status."