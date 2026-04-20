import pandas as pd
from processor import FlightProcessor


def main():
    flights = pd.read_csv("data/flights.csv")
    bookings = pd.read_csv("data/flight_bookings.csv")

    processor = FlightProcessor(flights, bookings)

    processor.validate_data()
    processor.allocate_seats()
    processor.generate_reports()

    print("Processing complete. Check output folder.")


if __name__ == "__main__":
    main()
