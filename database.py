import sqlite3
from datetime import datetime


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

#delete(after reading) from here
        self.tracking_number = "0000000569" # Валидация(според мен): len() <= 10 && без символи
        self.sender_name = "AAAA" #Валидация: len() < 0 && без цифри && без символи
        self.recipient_name = "BBBB" #Валидация: len() < 0 && без цифри && без символи
        self.origin_city = "CCCC" #Валидация: len() < 0 && без цифри && без символи
        self.destination_city = "DDDD" #Валидация: len() < 0 && без цифри && без символи
        self.weight = 20.94 #Валидация: weight > 0 && без символи
        self.current_status = "In transit" #Валидация: len() < 0 && без цифри && без символи
        self.status_history = "shipped" #Валидация: len() < 0 && без цифри && без символи
        # според мен трябва потребителя да избира от няколко статуса освен всеи път да си пише свой собствен
        """
        Registered: The shipper made a label, but the carrier does not have the package yet.
        Picked Up / Accepted: The delivery person has the package and starts the trip.
        In Transit: The package is moving between sorting hubs.
        Arrived at Hub: The package reached a local or regional sorting center.
        Customs Clearance: The package is being checked at a country border.
        Out for Delivery: The package is on the local delivery truck and will arrive today.
        Delivery Attempted: The driver tried to drop off the package, but no one was there or it was unsafe.
        Delivered: The package reached its final destination.
        Issues/Delayed: The package is behind schedule due to weather or traffic.
        Exception: An unexpected problem, like a damaged box or bad address, stopped the trip.
        """
        self.created_at = "11/02/2026"
# del to here

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
            return False
        except sqlite3.IntegrityError:
            print("SQLite error(err code:5): The tracking number already exists")
            return False

        return self.commit()



    # 6. SHOW All
    def print_all(self):
         try:
            self.cursor.execute("SELECT * FROM shipments;")
            shipments = self.cursor.fetchall()

            for packages in shipments:
                print(packages)
         except sqlite3.Error:
            print("SQLite error(err code:6): Problem with SELECT function or the printing of the table")

    # 7. show by tracking number
    def print_by_tracking_num(self, tracking_number):
        try:
            self.cursor.execute(
                "SELECT * FROM shipments WHERE tracking_number= ?;",
                (tracking_number,)
            )
            shipments = self.cursor.fetchall()

            for packages in shipments:
                print(packages)
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
            shipments = self.cursor.fetchone()[0]
            print(shipments)
        except sqlite3.Error:
            print("SQLite error(err code:8): Problem with SELECT function or the printing of the table")

    # 9-12. Update status
    def update_state(self, tracking_number, value):
        # 9. Взимане на current_status
        try:
            self.cursor.execute(
            """
                SELECT current_status FROM shipments WHERE tracking_number = ?;
            """,
                (tracking_number,)
            )

            current_status = self.cursor.fetchone()[0]
        except sqlite3.Error:
            print("SQLite error(err code:9): Problem with SELECT function or the printing of the table")
            return

        #10. Взимане на history_status
        try:
            self.cursor.execute(
            """
                SELECT status_history FROM shipments WHERE tracking_number = ?;
            """,
                (tracking_number,)
            )
            status_history = self.cursor.fetchone()[0]
        except sqlite3.Error:
            print("SQLite error(err code:10): Problem with SELECT function or the printing of the table")
            return

        #11. Обновяване на current_status
        try:
            self.cursor.execute(
                """
                   UPDATE shipments
                SET  current_status = ?
                WHERE tracking_number = ?; 
                """,
                    (datetime.now().strftime("%d/%m/%Y %H:%M:%S") + " - " + value, tracking_number)
            )
        except sqlite3.Error:
            print("SQLite error(err code:11): Problem with SELECT function or the printing of the table")
            self.conn.rollback()
            return

        #12. Обновяване на history_status = (history_status + current_staus)
        if current_status != status_history:
            try:
                self.cursor.execute(
                    """ 
                    UPDATE shipments
                    SET  status_history = ?
                    WHERE tracking_number = ?; 
                    """,
                    (str(status_history) + "\n" + str(current_status), tracking_number)
                )
                datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            except sqlite3.Error:
                print("SQLite error(err code:12): Problem with SELECT function or the printing of the table")
                self.conn.rollback()
                return
        self.print_status_history(tracking_number)
        self.commit()

    #13. DELETE
    def delete_package(self, tracking_number):
        try:
            self.cursor.execute(
                f"""
                DELETE FROM shipments WHERE tracking_number = ?;       
                """,
                    (tracking_number,)
            )
        except sqlite3.Error:
            print("SQLite error(err code:13): Problem with DELETE function")
            return

        print(f"You are currently deleting package - {tracking_number}!!!")
        self.commit()

    # 14. Затваряне на връзката
    def close_database(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            print("SQLite error(err code:14): Connection was not closed")
            exit(14)

        print("the connection was closed successfully")
