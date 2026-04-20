## Flight Booking & Seat Allocation Engine

# Objective

This project is a Python-based system to:

* Process flight bookings
* Validate booking data
* Allocate seats based on availability
* Handle overbooking using waitlisting
* Support booking cancellation with automatic waitlist promotion
* Generate reports

## Project Structure

.
├── data/
│   ├── flights.csv
│   └── flight_bookings.csv
├── output/
│   ├── booking_status_report.csv
│   └── flight_seat_summary.csv
├── tests/
│   └── test_processor.py
├── processor.py
├── utils.py
├── config.py
├── main.py
└── README.md

##  Features

###  Data Validation

Each booking is validated based on:

* Flight must exist
* seats_booked must be greater than 0
* booking_date must match format: dd-mm-yyyy


### Seat Allocation Logic

  Condition                   Status    

  Seats available ≥ requested  CONFIRMED 
  Seats partially available    PARTIAL   
  No seats available           WAITLIST  


### Cancellation & Auto-Promotion

* Only CONFIRMED or PARTIAL bookings can be cancelled
* Cancelling frees confirmed seats
* Freed seats are reassigned to waitlisted bookings automatically
* Promotion happens in booking order


### Output Reports

After execution, two CSV files are generated:

#### 1.booking_status_report.csv

Contains:

* booking_id
* flight_id
* seats_confirmed
* seats_waitlisted
* status

#### 2.flight_seat_summary.csv

Contains:

* flight_id
* total_seats
* remaining_seats


## How to Run

### 1.Install dependencies

pip install pandas

### 2.Run the application

python main.py


### 3. Run unit tests

python -m unittest discover tests


##  Test Coverage

The project includes unit tests for:

* Invalid flight rejection
* Negative seat rejection
* Seat allocation logic
* Waitlist handling
* Remaining seat calculation
* Partial allocation
* Cancellation logic
* Waitlist promotion


