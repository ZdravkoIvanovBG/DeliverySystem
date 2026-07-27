# 📚 Library
### A Python console application that allows staff to register and track shipments. Supports adding, searching, updating status, and deleting shipments, with concurrent processing of in-transit packages.

## Team & Contributions

**Team:** Zdravko, Momchil, Viktor

### Zdravko
- Built the `Shipment` class (`shipments.py`) with validation via getters/setters for all fields (tracking number, sender, recipient, cities, weight) and built 2 of the functions
- Implemented the concurrent processing feature (`workers.py`) using `ThreadPoolExecutor` to simulate simultaneous handling of in-transit shipments

### Momchil
- Designed and implemented the SQLite database layer (`database.py`), including the `DB` class: table creation, connection handling, and all CRUD operations (insert, select, update, delete)

### Viktor
- Built three of the functions (`shipments.py`)
- Built main.py and the menu

### Teamwork
- Added validations
- Fixed errors across the py files

# Project Setup Instructions

## Prerequisites

To run this project, you will need:

- Python 3.10+

## Setup Guide

### Step 1: Clone the Repository

First, clone the repository to your machine:

```sh
git clone <repository-url>
```

### Step 2: Navigate to the project directory 

```sh
cd <repository-directory>
```

### Step 3: Go into the main.py file

Go into the main.py file and run the program.

```sh
python main.py
```

---

## Database

The application uses SQLite (`sqlite3`) with a single table, `shipments`, stored in `shipments.db`.

### Table: `shipments`

| Column             | Type    | Constraints                  | Description                                  |
|---------------------|---------|-------------------------------|-----------------------------------------------|
| `id`                | INTEGER | PRIMARY KEY                  | Auto-incrementing row identifier              |
| `tracking_number`   | TEXT    | NOT NULL, UNIQUE             | Unique identifier for the shipment            |
| `sender_name`       | TEXT    | NOT NULL                     | Name of the sender                            |
| `recipient_name`    | TEXT    | NOT NULL                     | Name of the recipient                         |
| `origin_city`       | TEXT    | NOT NULL                     | City the shipment is sent from                |
| `destination_city`  | TEXT    | NOT NULL                     | City the shipment is being delivered to       |
| `weight`            | REAL    | NOT NULL, CHECK(weight > 0)  | Weight of the shipment in kg                  |
| `current_status`    | TEXT    | NOT NULL                     | The shipment's current status                 |
| `status_history`    | TEXT    | NOT NULL                     | Full log of status changes with timestamps    |
| `created_at`        | TEXT    | NOT NULL                     | Date and time the shipment was registered     |

All user-supplied values are inserted using parameterized queries (`?` placeholders) to prevent SQL injection. The `tracking_number` column's `UNIQUE` constraint enforces no two shipments can share the same tracking number; attempting to insert a duplicate raises `sqlite3.IntegrityError`, which the application catches and reports to the user.

The `status_history` column stores every status change for a shipment as a newline-separated, timestamped log — for example:

### How `ThreadPoolExecutor` Works

`ThreadPoolExecutor(max_workers=3)` creates a pool of 3 worker threads that can run tasks in parallel, instead of one after another.

```python
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(process_shipment, tracking_numbers)
```

- `executor.map(process_shipment, tracking_numbers)` runs `process_shipment` once for every tracking number in the list, distributing the work across the 3 available threads.
- Up to 3 shipments are processed simultaneously; if there are more than 3 tracking numbers, each worker picks up the next one as soon as it finishes its current task.
- `time.sleep()` inside `process_shipment` simulates processing time — while one thread is "waiting," the others continue running independently, which is what makes this faster than processing shipments one at a time.
- `executor.map()` blocks until all tasks are complete, then returns the results in the same order as the input list.
- The `with` block automatically closes the thread pool once all tasks finish, so no manual cleanup is needed.

This approach directly satisfies the requirement in the project specification (section 5) that shipment processing be handled concurrently using either `ThreadPoolExecutor` or a `Thread` subclass. `ThreadPoolExecutor` was chosen over manually managing individual `Thread` objects because it automatically handles thread creation, task distribution, and cleanup.

## Known Limitations

- **Tracking numbers are entered manually, not auto-generated.** The user is responsible for typing in a unique tracking number when adding a shipment. Uniqueness is only enforced at the database level (`UNIQUE` constraint), which raises an error and rejects the entry if a duplicate is used — there is no automatic generation of guaranteed-unique tracking numbers.
- **Optional/bonus features (section 10 of the assignment) are not implemented.** This includes search by name/city, filtering, sorting, editing shipment details, statistics (COUNT/SUM/AVG), automatic tracking number generation, and logging. Only the required functionality (section 9) is complete.