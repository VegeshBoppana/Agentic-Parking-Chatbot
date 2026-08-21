from langchain.tools import tool

from stage1_rag_chatbot.db.sql_store import get_available_spaces


@tool
def check_parking_availability(zone: str = "", vehicle_type: str = "") -> str:
    """Check live parking space availability and pricing. Optionally filter by
    zone (A, B, C, or D) and/or vehicle_type (Car, Motorcycle, EV, Disabled).
    Leave a field empty to search across all zones/vehicle types."""
    spaces = get_available_spaces(zone=zone or None, vehicle_type=vehicle_type or None)
    if not spaces:
        return "No available parking spaces found matching that criteria."

    prices = [s["price_per_hour"] for s in spaces]
    sample = spaces[:5]

    summary = (
        f"{len(spaces)} available space(s) found "
        f"(price range: Rs. {min(prices):.2f} - Rs. {max(prices):.2f}/hour).\n"
        "Sample spots:\n"
    )
    summary += "\n".join(
        f"- {s['spot_number']} (Zone {s['zone']}, Floor {s['floor']}, {s['vehicle_type']}, "
        f"Rs. {s['price_per_hour']:.2f}/hour)"
        for s in sample
    )
    return summary