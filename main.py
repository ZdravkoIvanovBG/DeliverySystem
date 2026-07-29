from database import DB
from shipments import (
    add_delivery, show_all_deliveries, search_by_tracking_number, change_status, show_history,
    delete_package, filter_shipments, Shipment  # filter_shipments, Shipment - добавени
)
from workers import process_undelivered_shipments, process_undelivered_shipments_with_threads  # вторият - нов
import colors  # добавено

db = DB()


def add_package_menu():
    tracking_number = input("Enter tracking number: ")
    sender_name = input("Enter sender name: ")
    recipient_name = input("Enter recipient name: ")
    origin_city = input("Enter origin city: ")
    destination_city = input("Enter destination city: ")

    try:
        weight = float(input("Enter weight: "))
    except ValueError:  # поправено: вече не гърми при текст
        print(colors.error("Моля, въведете валидно число."))
        return

    add_delivery(db, tracking_number, sender_name, recipient_name, origin_city, destination_city, weight)


def show_all_delivers():
    print(colors.title("All deliveries"))
    show_all_deliveries(db)


def search_by_tracking_number_menu():
    tracking_number = input("Enter tracking number: ")
    search_by_tracking_number(db, tracking_number)


def _choose_status():  # ново: помощна функция за филтъра по статус
    print(colors.title("Изберете статус:"))
    for i, status in enumerate(Shipment.ALLOWED_STATUSES, start=1):
        print(f"{i}. {status}")

    choice = input("Enter number (или Enter за без филтър по статус): ").strip()
    if choice == "":
        return None

    try:
        index = int(choice) - 1
        return Shipment.ALLOWED_STATUSES[index]
    except (ValueError, IndexError):
        print(colors.error("Невалиден избор."))
        return None


def change_status_menu():
    tracking_number = input("Enter tracking number: ")

    print(colors.title("Изберете нов статус:"))  # поправено: избор от списък, не свободен текст
    for i, status in enumerate(Shipment.ALLOWED_STATUSES, start=1):
        print(f"{i}. {status}")

    choice = input("Enter number: ")

    try:
        index = int(choice) - 1
        new_status = Shipment.ALLOWED_STATUSES[index]
    except (ValueError, IndexError):
        print(colors.error("Невалиден избор."))
        return

    change_status(db, tracking_number, new_status)


def show_history_menu():
    tracking_number = input("Enter tracking number: ")
    show_history(db, tracking_number)


def delete_package_menu():
    tracking_number = input("Enter tracking number: ")
    delete_package(db, tracking_number)


def process_multiple_undelivered_shipments_menu():
    tracking_numbers = db.get_undelivered_tracking_numbers()

    if len(tracking_numbers) < 3:
        print(colors.warning("Трябва да има поне 3 недоставени пратки."))
        return

    results = process_undelivered_shipments(tracking_numbers)

    for tracking_number, new_status in results:
        db.update_state(tracking_number, new_status)


def process_multiple_undelivered_shipments_thread_menu():  # ново
    tracking_numbers = db.get_undelivered_tracking_numbers()

    if len(tracking_numbers) < 3:
        print(colors.warning("Трябва да има поне 3 недоставени пратки."))
        return

    results = process_undelivered_shipments_with_threads(tracking_numbers)

    for tracking_number, new_status in results:
        db.update_state(tracking_number, new_status)


def filter_shipments_menu():  # ново
    status = _choose_status()

    city = input("Град (Enter за пропускане): ").strip() or None

    min_weight_input = input("Минимално тегло (Enter за пропускане): ").strip()
    min_weight = None
    if min_weight_input:
        try:
            min_weight = float(min_weight_input)
        except ValueError:
            print(colors.error("Невалидно тегло, филтърът по тегло се пропуска."))

    filter_shipments(db, status=status, city=city, min_weight=min_weight)


def main():
    is_running = True

    while is_running:
        print(colors.title("\n========= DELIVERY MENU ========="))
        print("1. Add a delivery")
        print("2. Show all deliveries")
        print("3. Search by tracking number")
        print("4. Filter deliveries")  # ново
        print("5. Change status")
        print("6. Show history")
        print("7. Delete package")
        print("8. Process multiple shipments (ThreadPoolExecutor)")
        print("9. Process multiple shipments (Thread class)")  # ново
        print("0. Exit")

        choice = input("Choose an option: ")

        match choice:
            case "1":
                add_package_menu()
            case "2":
                show_all_delivers()
            case "3":
                search_by_tracking_number_menu()
            case "4":
                filter_shipments_menu()
            case "5":
                change_status_menu()
            case "6":
                show_history_menu()
            case "7":
                delete_package_menu()
            case "8":
                process_multiple_undelivered_shipments_menu()
            case "9":
                process_multiple_undelivered_shipments_thread_menu()
            case "0":
                db.close_database()
                print(colors.success("Goodbye!"))
                is_running = False
            case _:
                print(colors.error("Invalid choice. Please try again."))


if __name__ == "__main__":
    main()