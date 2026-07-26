from database import DB
from shipments import add_delivery, show_all_deliveries, search_by_tracking_number, change_status, show_history, \
    delete_package
from workers import process_undelivered_shipments

db=DB()

def add_package_menu():
    tracking_number = input("Enter tracking number: ")
    sender_name = input("Enter sender name: ")
    recipient_name = input("Enter recipient name: ")
    origin_city = input("Enter origin city: ")
    destination_city = input("Enter destination city: ")
    weight = float(input("Enter weight: "))
    add_delivery(db, tracking_number, sender_name, recipient_name, origin_city, destination_city, weight)


def show_all_delivers():
    print("All deliveries")
    show_all_deliveries(db)

def search_by_tracking_number_menu():
    tracking_number=input("Enter tracking number: ")
    search_by_tracking_number(db, tracking_number)

def change_status_menu():
    tracking_number = input("Enter tracking number: ")
    new_status = input("Enter new status: ")
    change_status(db, tracking_number, new_status)

def show_history_menu():
    tracking_number = input("Enter tracking number: ")
    show_history(db, tracking_number)

def delete_package_menu():
    tracking_number = input("Enter tracking number: ")
    delete_package(db, tracking_number)

def process_multiple_undelivered_shipments_menu():

    tracking_numbers = db.get_undelivered_tracking_numbers()  # from database.py

    if len(tracking_numbers) < 3:
        print("Трябва да има поне 3 недоставени пратки.")
        return

    results = process_undelivered_shipments(tracking_numbers)

    for tracking_number, new_status in results:
        db.update_state(tracking_number, new_status)

def main():

    print("\n========= DELIVERY MENU =========")
    print("1. Add a delivery")
    print("2. Show all delivers")
    print("3. Search by tracking number")
    print("4. Change status")
    print("5. Show history")
    print("6. Delete package")
    print("7. Process multiple shipments")
    print("8. Exit")

    choice = input("Choose an option: ")

    match choice:
        case "1":
            add_package_menu()
        case "2":
            show_all_delivers()
        case "3":
            search_by_tracking_number_menu()
        case "4":
            change_status_menu()
        case "5":
            show_history_menu()
        case "6":
            delete_package_menu()
        case "7":
            process_multiple_undelivered_shipments_menu()
        case "8":
            db.close_database()
            print("Goodbye!")
            is_running = False
        case _:
            print("Invalid choice. Please try again.")

if "__main__" == __name__:
    main()
