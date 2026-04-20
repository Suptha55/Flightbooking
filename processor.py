import pandas as pd
from utils import is_valid_date


class FlightProcessor:
    def __init__(self, flights_df, bookings_df):
        self.flights = flights_df.copy()
        self.bookings = bookings_df.copy()

        # Normalize columns
        self.flights.columns = self.flights.columns.str.strip().str.lower()
        self.bookings.columns = self.bookings.columns.str.strip().str.lower()

        self.valid_bookings = None
        self.invalid_bookings = None
        self.flight_summary = None

    def validate_data(self):
        valid_rows = []
        invalid_rows = []

        flight_ids = set(self.flights["flight_id"])

        for _, row in self.bookings.iterrows():
            if row["flight_id"] not in flight_ids:
                invalid_rows.append(row)
                continue

            if row["seats_booked"] <= 0:
                invalid_rows.append(row)
                continue

            if not is_valid_date(str(row["booking_date"])):
                invalid_rows.append(row)
                continue

            valid_rows.append(row)

        self.valid_bookings = pd.DataFrame(valid_rows)
        self.invalid_bookings = pd.DataFrame(invalid_rows)

    def allocate_seats(self):
        flight_seats = self.flights.set_index("flight_id")["seat_capacity"].to_dict()
        remaining_seats = flight_seats.copy()

        if self.valid_bookings is None or self.valid_bookings.empty:
            self.valid_bookings = pd.DataFrame(
                columns=list(self.bookings.columns) + ["seats_confirmed", "seats_waitlisted", "status"]
            )
            summary = []
            for flight, total in flight_seats.items():
                summary.append({"flight_id": flight, "total_seats": total, "remaining_seats": total})
            self.flight_summary = pd.DataFrame(summary)
            return

        booking_status = []
        seats_confirmed_list = []
        seats_waitlisted_list = []

        for _, row in self.valid_bookings.iterrows():
            flight = row["flight_id"]
            seats_requested = int(row["seats_booked"])

            if seats_requested <= remaining_seats[flight]:
                status = "CONFIRMED"
                confirmed = seats_requested
                waitlisted = 0
                remaining_seats[flight] -= seats_requested

            elif remaining_seats[flight] > 0:
                status = "PARTIAL"
                confirmed = remaining_seats[flight]
                waitlisted = seats_requested - confirmed
                remaining_seats[flight] = 0

            else:
                status = "WAITLIST"
                confirmed = 0
                waitlisted = seats_requested

            booking_status.append(status)
            seats_confirmed_list.append(confirmed)
            seats_waitlisted_list.append(waitlisted)

        self.valid_bookings["seats_confirmed"] = seats_confirmed_list
        self.valid_bookings["seats_waitlisted"] = seats_waitlisted_list
        self.valid_bookings["status"] = booking_status

        summary = []
        for flight, total in flight_seats.items():
            summary.append({
                "flight_id": flight,
                "total_seats": total,
                "remaining_seats": remaining_seats[flight]
            })
        self.flight_summary = pd.DataFrame(summary)

    def cancel_booking(self, booking_id):
        mask = self.valid_bookings["booking_id"] == booking_id

        if not mask.any():
            return {"error": f"Booking {booking_id} not found."}

        row = self.valid_bookings[mask].iloc[0]

        if row["status"] not in ("CONFIRMED", "PARTIAL"):
            return {"error": f"Booking {booking_id} is '{row['status']}' — cannot cancel."}

        flight_id = row["flight_id"]
        freed_seats = int(row["seats_confirmed"])

        # Cancel booking
        self.valid_bookings.loc[mask, "status"] = "CANCELLED"
        self.valid_bookings.loc[mask, "seats_confirmed"] = 0
        self.valid_bookings.loc[mask, "seats_waitlisted"] = 0

        # Free seats
        flight_mask = self.flight_summary["flight_id"] == flight_id
        self.flight_summary.loc[flight_mask, "remaining_seats"] += freed_seats
        available_seats = int(self.flight_summary.loc[flight_mask, "remaining_seats"].iloc[0])

        # Promote waitlist
        waitlist_mask = (
            (self.valid_bookings["flight_id"] == flight_id) &
            (self.valid_bookings["status"].isin(["WAITLIST", "PARTIAL"]))
        )
        waitlist_df = self.valid_bookings[waitlist_mask]

        promoted = []

        for idx, waitlist_row in waitlist_df.iterrows():
            if available_seats <= 0:
                break

            needed = int(waitlist_row["seats_waitlisted"])

            if needed <= available_seats:
                self.valid_bookings.loc[idx, "seats_confirmed"] += needed
                self.valid_bookings.loc[idx, "seats_waitlisted"] = 0
                self.valid_bookings.loc[idx, "status"] = "CONFIRMED"
                available_seats -= needed
            else:
                self.valid_bookings.loc[idx, "seats_confirmed"] += available_seats
                self.valid_bookings.loc[idx, "seats_waitlisted"] -= available_seats
                self.valid_bookings.loc[idx, "status"] = "PARTIAL"
                available_seats = 0

            promoted.append(str(waitlist_row["booking_id"]))

        self.flight_summary.loc[flight_mask, "remaining_seats"] = available_seats

        return {
            "cancelled": booking_id,
            "flight_id": flight_id,
            "freed_seats": freed_seats,
            "promoted": promoted,
            "remaining_seats_after": available_seats
        }

    def generate_reports(self):
        self.valid_bookings.to_csv("output/booking_status_report.csv", index=False)
        self.flight_summary.to_csv("output/flight_seat_summary.csv", index=False)