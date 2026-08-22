"""Temporary standalone test - calls Stage 3's agent directly, no Stage 1/2 involved."""

from stage3_mcp_server.agent import write_confirmed_reservation

write_confirmed_reservation(
    name="Direct Test",
    car_number="TS00ZZ0000",
    reservation_period="2026-08-23T10:00:00 to 2026-08-23T11:00:00",
    approval_time="2026-08-23T09:00:00",
)
print("Done - check stage3_mcp_server/data/confirmed_reservations.txt")