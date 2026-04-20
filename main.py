import pandas as pd
from processor import FlightProcessor


def main():
    flights = pd.read_csv("data/flights.csv")
    bookings = pd.read_csv("data/flight_bookings.csv")

    processor = FlightProcessor(flights, bookings)

    processor.validate_data()
    processor.allocate_seats()

    # Try cancelling a booking
    result = processor.cancel_booking("B001")

    if "error" in result:
        print(f"Cancellation failed: {result['error']}")
    else:
        print(f"Cancelled booking : {result['cancelled']}")
        print(f"Freed seats       : {result['freed_seats']} on flight {result['flight_id']}")
        if result["promoted"]:
            print(f"Promoted from waitlist: {', '.join(result['promoted'])}")
        else:
            print("No waitlisted bookings were promoted.")
        print(f"Remaining seats after: {result['remaining_seats_after']}")

    processor.generate_reports()
    print("\nProcessing complete. Check output folder.")


if __name__ == "__main__":
    main()