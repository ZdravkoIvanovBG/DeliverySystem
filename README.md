# 📚 Library
### A Python console application that allows staff to register and track shipments. Supports adding, searching, filtering, sorting, editing, updating status, and deleting shipments, with concurrent processing of in-transit packages and colored console output.

## Team & Contributions

**Team:** Zdravko, Momchil, Viktor

### Zdravko
- Built the `Shipment` class (`shipments.py`) with validation via getters/setters for all fields (tracking number, sender, recipient, cities, weight), plus part of the functions in `shipments.py`
- Implemented the concurrent processing feature (`workers.py`) using `ThreadPoolExecutor` to simulate simultaneous handling of in-transit shipments, plus an alternative implementation using a custom `Thread` subclass (`ShipmentWorker`)
- Implemented most of the bonus, database-side logic in `database.py`: filtering, sorting, search by name/town, average/sum weight, count by status, and field editing

### Momchil
- Designed and implemented the core SQLite database layer (`database.py`), including the `DB` class: table creation, connection handling, and the core CRUD operations (insert, select, update, delete)

### Viktor
- Built part of the functions in `shipments.py`
- Built `main.py` and the menu
- Added colored console output (`colors.py`) for menus and messages (success, error, warning, info)
- Added application logging (`logger.py`), writing key actions (creation, status updates, edits, deletions, errors) to `app.log`

### Teamwork
- Added validations
- Fixed errors across the py files
- Implemented all optional/bonus features from section 10 of the assignment

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

```
31/07/2026 10:12:03 - Регистрирана
31/07/2026 10:15:47 - Приета в офис
31/07/2026 11:02:19 - Транспортира се
```

Every change requires manual confirmation (`Y/N`) before being committed to the database via the `DB.commit()` method; answering `N` rolls back the pending change instead.

## Features

The console menu (`main.py`) exposes the following options:

1. **Add a delivery** — registers a new shipment with input validation (non-empty text fields, letters/spaces/hyphens only for names and cities, positive numeric weight).
2. **Show all deliveries** — lists every shipment currently in the database.
3. **Search by tracking number** — looks up a single shipment by its unique tracking number.
4. **Filter deliveries** *(bonus)* — filters shipments by any combination of status, city (origin or destination, partial match), and minimum weight.
5. **Change status** — updates a shipment's `current_status` to one of the predefined `Shipment.ALLOWED_STATUSES` and appends the change to its history.
6. **Show history** — prints the full timestamped status history of a shipment.
7. **Delete package** — removes a shipment from the database.
8. **Process multiple shipments (ThreadPoolExecutor)** — concurrently advances the status of several undelivered shipments using a thread pool.
9. **Process multiple shipments (Thread class)** *(bonus)* — same concurrent processing, implemented manually with a `Thread` subclass instead of `ThreadPoolExecutor`.
10. **Order deliveries** *(bonus)* — sorts all shipments by weight, date, or origin city, in ascending or descending order.
11. **Search by name or town** *(bonus)* — finds shipments by sender name or origin city (partial, case-insensitive match).
12. **Average weight of all deliveries** *(bonus)* — calculates the average weight across all registered shipments.
13. **Sum of total weight of all deliveries** *(bonus)* — calculates the combined weight of all registered shipments.
14. **Count deliveries by status** *(bonus)* — counts shipments, optionally filtered by a specific status.
15. **Edit delivery** *(bonus)* — edits the sender, recipient, origin city, destination city, or weight of an existing shipment.
0. **Exit** — closes the database connection and exits the program.

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

This approach directly satisfies the requirement in the project specification (section 5) that shipment processing be handled concurrently using either `ThreadPoolExecutor` or a `Thread` subclass.

### How the `Thread` class alternative works

As a bonus, `workers.py` also includes `ShipmentWorker`, a custom subclass of `Thread`:

```python
class ShipmentWorker(Thread):
    def __init__(self, tracking_number):
        Thread.__init__(self)
        self.tracking_number = tracking_number
        self.result = None

    def run(self):
        self.result = process_shipment(self.tracking_number)
```

- A separate `ShipmentWorker` thread is created for every selected shipment.
- `start()` launches each thread without blocking, so all shipments begin processing at roughly the same time (there is no fixed pool size limiting concurrency, unlike `ThreadPoolExecutor`).
- `join()` is then called on every worker to wait until all of them have finished before collecting results.
- Each worker stores its own result on `self.result`, which is read back once every thread has completed.

This gives the same end result as the `ThreadPoolExecutor` version, but with the thread lifecycle (creation, starting, and joining) managed explicitly instead of by an executor.

## Logging

`logger.py` configures a shared logger (`shipment_tracker`) that writes timestamped `INFO`/`WARNING`/`ERROR` entries to `app.log`. The database layer (`database.py`) logs key events, including:

- Successful shipment creation
- Failed inserts and duplicate tracking numbers
- Status updates
- Successful and failed edits
- Shipment deletions

## Colored Console Output

`colors.py` wraps console text in ANSI escape codes and provides helper functions (`success`, `error`, `warning`, `info`, `title`, `menu_item`, `menu_exit`) used throughout `main.py` and `shipments.py` to make menus and messages easier to read at a glance (green for success, red for errors, yellow for warnings, cyan for info).

## Known Limitations

- **Tracking numbers are entered manually, not auto-generated.** The user is responsible for typing in a unique tracking number when adding a shipment. Uniqueness is only enforced at the database level (`UNIQUE` constraint), which raises an error and rejects the entry if a duplicate is used — there is no automatic generation of guaranteed-unique tracking numbers.