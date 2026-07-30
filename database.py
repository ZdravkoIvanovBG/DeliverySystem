import sqlite3
from datetime import datetime
from logger import logger  # добавено: логване на действията


class DB:
    def __init__(self):
        # 1. Свързване с базата данни (ако файлът не съществува, ще се създаде автоматично)
        try:
            self.conn = sqlite3.connect("shipments.db")
        except sqlite3.Error:
            print("SQLite error(err code:1): The database couldn't load correctly")
            exit(1)

        # 2. Създаване на курсор
        try:
            self.cursor = self.conn.cursor()
        except sqlite3.Error:
            print("SQLite error(err code:2): cursor wasn't able to be created correctly")
            exit(2)

        print("The connection with the database was successful")

        # 3. Създаване на таблица

        # Проверява дали теглото е положително число
        # Current_status и Status_history винаги започва като 'Registered'
        # На Created_at автоматично задава днешна дата
        try:
            self.cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS "shipments" (
                "id" INTEGER PRIMARY KEY,
                "tracking_number"	TEXT NOT NULL UNIQUE,
                "sender_name"	TEXT NOT NULL,
                "recipient_name"	TEXT NOT NULL,
                "origin_city"	TEXT NOT NULL,
                "destination_city"	TEXT NOT NULL,
                "weight"	REAL NOT NULL CHECK(Weight > 0),  
                "current_status"	TEXT NOT NULL, 
                "status_history"	TEXT NOT NULL,    
                "created_at"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
            )

        except sqlite3.Error:
            print("SQLite error(err code:3): Table was not created")
            exit(3)

        print("The table was loaded successfully")

    # 4. Commit
    def commit(self):
        while True:
            print("Are you sure you want to save changes?: Y/N")
            answer = input()
            if answer.lower().strip() == 'y':
                try:
                    self.conn.commit()
                except sqlite3.Error:
                    print("SQLite error(err code:4): The database wasn't saved correctly")
                    exit(4)
                return True

            elif answer.lower().strip() == 'n':
                self.conn.rollback()
                return False

            else:
                print("Invalid input")

    # 5. Създаване на нова пратка
    def create_package(self, shipment):
        try:
            self.cursor.execute(
            """
            INSERT INTO shipments(tracking_number, sender_name, recipient_name, origin_city, destination_city, weight, current_status, status_history, created_at)
            VALUES(?,?,?,?,?,?,?,?, ?);
            """,
                (
                 shipment.tracking_number,
                 shipment.sender_name,
                 shipment.recipient_name,
                 shipment.origin_city,
                 shipment.destination_city,
                 shipment.weight,
                 shipment.current_status,
                 shipment.status_history,
                 shipment.created_at
                 )
            )
        except sqlite3.OperationalError:
            print("SQLite error(err code:5): Insert function wasn't able to be implemented correctly")
            logger.error(f"Insert failed for tracking_number={shipment.tracking_number}")  # добавено
            return False
        except sqlite3.IntegrityError:
            print("SQLite error(err code:5): The tracking number already exists")
            logger.warning(f"Duplicate tracking_number={shipment.tracking_number}")  # добавено
            return False

        result = self.commit()
        if result:
            logger.info(f"Shipment created: {shipment.tracking_number}")  # добавено
        return result

    # 6. SHOW All
    def print_all(self):
         try:
            self.cursor.execute("SELECT tracking_number, origin_city, destination_city, weight, current_status  FROM shipments;")
            shipments = self.cursor.fetchall()

            return shipments

         except sqlite3.Error:
            print("SQLite error(err code:6): Problem with SELECT function or the printing of the table")

    # 7. show by tracking number
    def print_by_tracking_num(self, tracking_number):
        try:
            self.cursor.execute(
                "SELECT tracking_number, sender_name, recipient_name, origin_city, destination_city, weight, current_status "
                "FROM shipments "
                "WHERE tracking_number= ?;",
                (tracking_number,)
            )

            return self.cursor.fetchall()

        except sqlite3.Error:
            print("SQLite error(err code:7): Problem with SELECT function or the printing of the table")

    # 8. show tracking history
    def print_status_history(self, tracking_number):
        try:
            self.cursor.execute(
            """
                SELECT status_history FROM shipments WHERE tracking_number = ?;
            """,
                (tracking_number,)
            )

            shipments_row = self.cursor.fetchone()

            if shipments_row is None:
                return None

            return shipments_row[0]
        except sqlite3.Error:
            print("SQLite error(err code:8): Problem with SELECT function or the printing of the table")

    # 9-12. Update status
    def update_state(self, tracking_number, new_status):
        #10. Взимане на status_history
        try:
            self.cursor.execute(
            """
                SELECT status_history FROM shipments WHERE tracking_number = ?;
            """,
                (tracking_number,)
            )
            status_history = self.cursor.fetchone()

            if not status_history:
                return None

            status_history = status_history[0]

        except sqlite3.Error:
            print("SQLite error(err code:10): Problem with SELECT function or the printing of the table")
            return

        changed_at_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        new_status_history = status_history + "\n" + f"{changed_at_time} - {new_status}"

        #11. Обновяване на current_status
        try:
            self.cursor.execute(
                """
                   UPDATE shipments
                SET  current_status = ?
                WHERE tracking_number = ?;
                """,
                    (new_status, tracking_number)
            )
        except sqlite3.Error:
            print("SQLite error(err code:11): Problem with SELECT function or the printing of the table")
            self.conn.rollback()
            return

        #12. Обновяване на history_status = (history_status + current_staus)
        try:
            self.cursor.execute(
                """
                UPDATE shipments
                SET  status_history = ?
                WHERE tracking_number = ?;
                """,
                (new_status_history, tracking_number)
            )

        except sqlite3.Error:
            print("SQLite error(err code:12): Problem with SELECT function or the printing of the table")
            self.conn.rollback()
            return

        self.print_status_history(tracking_number)
        result = self.commit()
        if result:
            logger.info(f"Status updated: {tracking_number} -> {new_status}")  # добавено
        return result

    #13. DELETE
    def delete_package(self, tracking_number):
        try:
            self.cursor.execute(
                f"""
                DELETE FROM shipments WHERE tracking_number = ?;       
                """,
                    (tracking_number,)
            )
            if self.cursor.rowcount == 0:
                print("No shipments found with the given tracking number.")
                return False
        except sqlite3.Error:
            print("SQLite error(err code:13): Problem with DELETE function")
            return False

        print(f"You are currently deleting package - {tracking_number}!!!")
        result = self.commit()
        if result:
            logger.info(f"Shipment deleted: {tracking_number}")  # добавено
        return result

    # 14. Затваряне на връзката
    def close_database(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            print("SQLite error(err code:14): Connection was not closed")
            exit(14)

        print("the connection was closed successfully")

    # 15. Връщане на всички недоставени пратки
    def get_undelivered_tracking_numbers(self):
        try:
            self.cursor.execute(
                f"""
                SELECT tracking_number FROM shipments WHERE current_status != ?;       
                """,
                    ("Доставена",)
            )
            rows = self.cursor.fetchall()

            return list(map(lambda row: row[0], rows))
        except sqlite3.Error:
            print("SQLite error(err code:15): Problem with SELECT function")
            return []

    # 16. Филтриране по статус, град и/или минимално тегло (ново, допълнителна задача)
    def filter_shipments(self, status=None, city=None, min_weight=None):
        try:
            query = (
                "SELECT tracking_number, origin_city, destination_city, weight, current_status "
                "FROM shipments WHERE 1=1"
            )
            params = []

            if status:
                query += " AND current_status = ?"
                params.append(status)
            if city:
                query += " AND (origin_city LIKE ? COLLATE NOCASE OR destination_city LIKE ? COLLATE NOCASE)"
                params.extend([f"%{city}%", f"%{city}%"])
            if min_weight is not None:
                query += " AND weight >= ?"
                params.append(min_weight)

            query += ";"
            self.cursor.execute(query, tuple(params))
            return self.cursor.fetchall()
        except sqlite3.Error as error:
            print(f"SQLite error(err code:16): {error}")
            return []

    def order_deliveries_by_weight_date_city(self, sort_by, direction):
        columns = {
            'weight': 'weight',
            'date': 'created_at',
            'city': 'origin_city'
        }

        sort_by_column = columns[sort_by]
        sort_direction = 'DESC' if direction == "d" else 'ASC'

        try:
            self.cursor.execute(
                f"""
                SELECT tracking_number, origin_city, destination_city, weight, current_status, created_at
                FROM shipments
                ORDER BY {sort_by_column} {sort_direction};
                """,
            )

            return self.cursor.fetchall()
        except sqlite3.Error:
            print("SQLite error(err code:19): Problem with SELECT function")
            return None

    def search_by_name_or_town(self, search_term):
        try:
            search_pattern = f"%{search_term}%"
            self.cursor.execute(
                """
                SELECT tracking_number, sender_name, origin_city, destination_city, weight, current_status
                FROM shipments 
                WHERE sender_name 
                    LIKE ? COLLATE NOCASE
                   OR origin_city 
                    LIKE ? COLLATE NOCASE
                """,
                (search_pattern, search_pattern)
            )

            return self.cursor.fetchall()
        except sqlite3.Error:
            print("SQLite error(err code:18): Problem with SELECT function")
            return None

    def average_weight(self):
        try:
            self.cursor.execute("SELECT AVG(weight) FROM shipments;")

            avg_weight = self.cursor.fetchone()[0]

            if not avg_weight:
                return 0

            return avg_weight
        except sqlite3.Error:
            print("SQLite error(err code:17): Problem with SELECT function")
            return None

    def sum_total_weight(self):
        try:
            self.cursor.execute("SELECT SUM(weight) FROM shipments;")

            total_weight = self.cursor.fetchone()[0]

            if not total_weight:
                return 0

            return total_weight

        except sqlite3.Error:
            print("SQLite error(err code:17): Problem with SELECT function")
            return None

    def count_deliveries(self, status):
        try:
            if status:
                self.cursor.execute(
                    f"""
                SELECT COUNT(*) FROM shipments WHERE current_status = ?;
                """,
                    (status,)
                )
            else:
                self.cursor.execute("SELECT COUNT(*) FROM shipments;")

            count = self.cursor.fetchone()[0]
            return count
        except sqlite3.Error:
            print("SQLite error(err code:16): Problem with SELECT function")
            return None

    def edit_delivery_field(self, tracking_number, field, new_value):
        allowed_field = {
            "sender": "sender_name",
            "recipient": "recipient_name",
            "origin city": "origin_city",
            "destination city": "destination_city",
            "weight": "weight"
        }

        column = allowed_field[field]

        try:
            self.cursor.execute(
                f"""
                UPDATE shipments SET {column} = ? WHERE tracking_number = ?;
                """,
                (new_value, tracking_number)
            )

            if self.cursor.rowcount == 0:
                logger.warning(f"Edit failed: Tracking number {tracking_number} not found")
                return None

        except sqlite3.Error:
            print("SQLite error(err code:20): Problem with UPDATE function")
            logger.error(f"Edit failed for tracking_number={tracking_number}, field={field}")
            return False

        result = self.commit()
        if result:
            logger.info(f"Shipment edited: {tracking_number} -> {field} changed to '{new_value}'")
        return result

    def get_status_by_tracking_number(self, tracking_number):
        try:
            self.cursor.execute(
                """
                SELECT current_status FROM shipments WHERE tracking_number = ?;
                """,
                (tracking_number,)
            )
        except sqlite3.Error:
            print("SQLite error(err code:21): Problem with SELECT function")
            return None

        return self.cursor.fetchone()[0]
