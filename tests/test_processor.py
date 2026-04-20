import unittest
import pandas as pd
from processor import FlightProcessor


class TestFlightProcessor(unittest.TestCase):

    def setUp(self):
        self.valid_date = "01-01-2024"
        
    def test_invalid_flight_rejected(self):
        flights = pd.DataFrame({"flight_id": ["F001"], "seat_capacity": [100]})
        bookings = pd.DataFrame({
            "booking_id": ["B001"],
            "flight_id": ["F999"],
            "user_id": ["U001"],
            "seats_booked": [10],
            "booking_date": [self.valid_date]
        })

        fp = FlightProcessor(flights, bookings)
        fp.validate_data()

        self.assertEqual(len(fp.valid_bookings), 0)

    def test_negative_seats_rejected(self):
        flights = pd.DataFrame({"flight_id": ["F001"], "seat_capacity": [100]})
        bookings = pd.DataFrame({
            "booking_id": ["B001"],
            "flight_id": ["F001"],
            "user_id": ["U001"],
            "seats_booked": [-5],
            "booking_date": [self.valid_date]
        })

        fp = FlightProcessor(flights, bookings)
        fp.validate_data()

        self.assertEqual(len(fp.valid_bookings), 0)

    def test_seat_allocation(self):
        flights = pd.DataFrame({"flight_id": ["F001"], "seat_capacity": [100]})
        bookings = pd.DataFrame({
            "booking_id": ["B001"],
            "flight_id": ["F001"],
            "user_id": ["U001"],
            "seats_booked": [50],
            "booking_date": [self.valid_date]
        })

        fp = FlightProcessor(flights, bookings)
        fp.validate_data()
        fp.allocate_seats()

        self.assertEqual(fp.valid_bookings.iloc[0]["status"], "CONFIRMED")

    def test_waitlist_logic(self):
        flights = pd.DataFrame({"flight_id": ["F001"], "seat_capacity": [50]})
        bookings = pd.DataFrame({
            "booking_id": ["B001"],
            "flight_id": ["F001"],
            "user_id": ["U001"],
            "seats_booked": [100],
            "booking_date": [self.valid_date]
        })

        fp = FlightProcessor(flights, bookings)
        fp.validate_data()
        fp.allocate_seats()

        self.assertEqual(fp.valid_bookings.iloc[0]["status"], "PARTIAL")

    def test_remaining_seats_calculation(self):
        flights = pd.DataFrame({"flight_id": ["F001"], "seat_capacity": [100]})
        bookings = pd.DataFrame({
            "booking_id": ["B001"],
            "flight_id": ["F001"],
            "user_id": ["U001"],
            "seats_booked": [40],
            "booking_date": [self.valid_date]
        })

        fp = FlightProcessor(flights, bookings)
        fp.validate_data()
        fp.allocate_seats()

        remaining = fp.flight_summary.iloc[0]["remaining_seats"]
        self.assertEqual(remaining, 60)

  # New feature tests

    def test_partial_allocation(self):
        flights = pd.DataFrame({"flight_id": ["F001"], "seat_capacity": [50]})
        bookings = pd.DataFrame({
            "booking_id": ["B001"],
            "flight_id": ["F001"],
            "user_id": ["U001"],
            "seats_booked": [70],
            "booking_date": [self.valid_date]
        })

        fp = FlightProcessor(flights, bookings)
        fp.validate_data()
        fp.allocate_seats()

        row = fp.valid_bookings.iloc[0]
        self.assertEqual(row["status"], "PARTIAL")
        self.assertEqual(row["seats_confirmed"], 50)
        self.assertEqual(row["seats_waitlisted"], 20)

    def test_cancellation_and_promotion(self):
        flights = pd.DataFrame({"flight_id": ["F001"], "seat_capacity": [50]})
        bookings = pd.DataFrame({
            "booking_id": ["B001", "B002"],
            "flight_id": ["F001", "F001"],
            "user_id": ["U001", "U002"],
            "seats_booked": [50, 30],
            "booking_date": [self.valid_date, self.valid_date]
        })

        fp = FlightProcessor(flights, bookings)
        fp.validate_data()
        fp.allocate_seats()

        # B001 CONFIRMED, B002 WAITLIST/PARTIAL
        result = fp.cancel_booking("B001")

        self.assertEqual(result["freed_seats"], 50)

        # B002 should now be promoted
        updated = fp.valid_bookings[fp.valid_bookings["booking_id"] == "B002"].iloc[0]
        self.assertEqual(updated["status"], "CONFIRMED")

    def test_cancel_invalid_booking(self):
        flights = pd.DataFrame({"flight_id": ["F001"], "seat_capacity": [50]})
        bookings = pd.DataFrame({
            "booking_id": ["B001"],
            "flight_id": ["F001"],
            "user_id": ["U001"],
            "seats_booked": [10],
            "booking_date": [self.valid_date]
        })

        fp = FlightProcessor(flights, bookings)
        fp.validate_data()
        fp.allocate_seats()

        result = fp.cancel_booking("B999")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()