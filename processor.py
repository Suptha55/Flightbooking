import pandas as pd
from utils import is_valid_date


class FlightProcessor:
    def __init__(self, flights_df, bookings_df):
        self.flights = flights_df.copy()
        self.bookings = bookings_df.copy()

        # Normalize columns
        self.flights.columns = self.flights.columns.str.strip().str.lower()
        self.bookings.columns = self.bookings.columns.str.strip().str.lower()

        # flights.csv → flight_id, airline, source, destination, seat_capacity
        # bookings.csv → booking_id, flight_id, user_id, seats_booked, booking_date

        self.valid_bookings = None
        self.invalid_bookings = None
        self.flight_summary = None   # ✅ always initialize

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

        # Case 1: No valid bookings
        if self.valid_bookings is None or self.valid_bookings.empty:
            self.valid_bookings = pd.DataFrame(columns=list(self.bookings.columns) + ["status"])

            summary = []
            for flight, total in flight_seats.items():
                summary.append({
                    "flight_id": flight,
                    "total_seats": total,
                    "remaining_seats": total
                })

            self.flight_summary = pd.DataFrame(summary)
            return

        # Case 2: Normal processing
        booking_status = []

        for _, row in self.valid_bookings.iterrows():
            flight = row["flight_id"]
            seats_requested = row["seats_booked"]

            if seats_requested <= remaining_seats[flight]:
                status = "CONFIRMED"
                remaining_seats[flight] -= seats_requested
            else:
                status = "WAITLIST"

            booking_status.append(status)

        # Add status column
        self.valid_bookings["status"] = booking_status

        # Create flight summary
        summary = []
        for flight, total in flight_seats.items():
            remaining = remaining_seats[flight]
            summary.append({
                "flight_id": flight,
                "total_seats": total,
                "remaining_seats": remaining
            })

        self.flight_summary = pd.DataFrame(summary)

    def generate_reports(self):
        self.valid_bookings.to_csv("output/booking_status_report.csv", index=False)
        self.flight_summary.to_csv("output/flight_seat_summary.csv", index=False)