from database import DB
from shipments import (
    add_delivery, show_all_deliveries, search_by_tracking_number, change_status, show_history,
    delete_package, filter_shipments, Shipment, order_deliveries,
    search_by_name_or_town, average_weight, sum_total_weight, count_deliveries,
    edit_delivery  # filter_shipments, Shipment - добавени
)
from workers import process_undelivered_shipments, process_undelivered_shipments_with_threads  # вторият - нов
import colors  # добавено

db = DB()


def get_valid_text(message):
    while True:
        user_input = input(message).strip()

        # 1. Check for empty string
        if not user_input:
            print(colors.warning("Error: Input cannot be empty. Please try again."))
            continue

        # 2. Check if the input is a number (positive, negative, or decimal)
        try:
            float(user_input)
            # If the above line succeeds, it means they entered a pure number
            print(colors.warning("Error: Input cannot be just a number. Please enter valid text."))
            continue
        except ValueError:
            pass

        has_valid_chars = all(char.isalnum() or char.isspace() or char == '-' for char in user_input)

        if not has_valid_chars:
            print(colors.warning("Error: Input cannot contain special symbols like %, ^, &, etc. Please try again."))
            continue

        return user_input

def add_package_menu():
    tracking_number = get_valid_text("Enter tracking number: ")
    sender_name = get_valid_text("Enter sender name: ")
    recipient_name = get_valid_text("Enter recipient name: ")
    origin_city = get_valid_text("Enter origin city: ")
    destination_city = get_valid_text("Enter destination city: ")

    while True:
        try:
            weight = float(input("Enter weight: "))

            if weight <= 0:
                raise ValueError

            break
        except ValueError:  # поправено: вече не гърми при текст
            print(colors.warning("Please, enter a valid weight."))

    add_delivery(db, tracking_number, sender_name, recipient_name, origin_city, destination_city, weight)


def show_all_delivers():
    print(colors.title("All deliveries"))
    show_all_deliveries(db)


def search_by_tracking_number_menu():
    tracking_number = input("Enter tracking number: ").strip()
    search_by_tracking_number(db, tracking_number)


def _choose_status():  # ново: помощна функция за филтъра по статус
    print(colors.title("Choose status:"))
    for i, status in enumerate(Shipment.ALLOWED_STATUSES, start=1):
        print(colors.menu_item(i, status))

    while True:
        choice = input(colors.info("Enter number (или Enter за без филтър по статус): ")).strip()
        if choice == "":
            return None

        try:
            index = int(choice) - 1

            if index < 0:
                raise IndexError

            return Shipment.ALLOWED_STATUSES[index]
        except (ValueError, IndexError):
            print(colors.error("Invalid choice."))
            pass

def change_status_menu():
    tracking_number = input("Enter tracking number: ").strip()

    new_status = _choose_status()

    change_status(db, tracking_number, new_status)

def show_history_menu():
    tracking_number = input("Enter tracking number: ").strip()
    show_history(db, tracking_number)


def delete_package_menu():
    tracking_number = input("Enter tracking number: ").strip()
    delete_package(db, tracking_number)


def process_multiple_undelivered_shipments_menu():
    tracking_numbers = db.get_undelivered_tracking_numbers()

    if len(tracking_numbers) < 3:
        print(colors.warning("There has to be at least 3 undelivered shipments to process them."))
        return

    results = process_undelivered_shipments(tracking_numbers)

    for tracking_number, new_status in results:
        db.update_state(tracking_number, new_status)


def process_multiple_undelivered_shipments_thread_menu():  # ново
    tracking_numbers = db.get_undelivered_tracking_numbers()

    if len(tracking_numbers) < 3:
        print(colors.warning("There has to be at least 3 undelivered shipments to process them."))
        return

    results = process_undelivered_shipments_with_threads(tracking_numbers)

    for tracking_number, new_status in results:
        db.update_state(tracking_number, new_status)


def filter_shipments_menu():  # ново
    status = _choose_status()

    city = input("City (Enter за пропускане): ").strip() or None

    min_weight_input = input("Minimum Weight (Enter за пропускане): ").strip()
    min_weight = None
    if min_weight_input:
        try:
            min_weight = float(min_weight_input)
        except ValueError:
            print(colors.error("Invalid weight, skipping filtering by weight."))

    filter_shipments(db, status=status, city=city, min_weight=min_weight)

def order_deliveries_menu():
    valid_options = ["weight", "date", "city"]

    while True:
        sort_by = input("Sort by (weight, date, city): ").lower().strip()

        if sort_by in valid_options:
            break

        print(colors.error("Invalid option. Please choose from the available options."))

    while True:
        direction = input("Direction (d for descending, a for ascending): ").lower().strip()

        if direction in ["d", "a"]:
            break

        print(colors.error("Invalid direction. Please choose 'd' for descending or 'a' for ascending."))

    order_deliveries(db, sort_by, direction)

def search_by_name_or_town_menu():
    search_term = input("Please enter a sender name or a town name: ")

    search_by_name_or_town(db, search_term)

def average_weight_menu():
    average_weight(db)

def sum_total_weight_menu():
    sum_total_weight(db)

def count_deliveries_menu():
    status = _choose_status()

    count_deliveries(db, status)

def edit_delivery_menu():
    tracking_number = input("Enter tracking number: ").strip()

    allowed_field = ["sender", "recipient", "origin city", "destination city", "weight"]

    while True:
        field = input("Enter field to edit (sender, recipient, origin city, destination city, weight): ").lower().strip()

        if field in allowed_field:
            break

        print(colors.error("Invalid field. Please choose from the available options."))

    while True:
        new_value = get_valid_text(f"Enter new value for {field}: ")

        if field == "weight":
            try:
                new_value = float(new_value)

                if new_value <= 0:
                    raise ValueError

                break
            except ValueError:
                print(colors.error("Invalid weight value. Please enter a valid number."))
                continue

        if new_value.strip() == "":
            print(colors.error("Value cannot be empty."))
        else:
            break

    edit_delivery(db, tracking_number, field, new_value)

def main():
    is_running = True

    while is_running:
        print(colors.title("\n========= DELIVERY MENU ========="))
        print(colors.menu_item(1, "Add a delivery"))
        print(colors.menu_item(2, "Show all deliveries"))
        print(colors.menu_item(3, "Search by tracking number"))
        print(colors.menu_item(4, "Filter deliveries"))  # ново
        print(colors.menu_item(5, "Change status"))
        print(colors.menu_item(6, "Show history"))
        print(colors.menu_item(7, "Delete package"))
        print(colors.menu_item(8, "Process multiple shipments (ThreadPoolExecutor)"))
        print(colors.menu_item(9, "Process multiple shipments (Thread class)"))  # ново
        print(colors.menu_item(10, "Order deliveries"))
        print(colors.menu_item(11, "Search by name or town"))
        print(colors.menu_item(12, "Average weight of all deliveries"))
        print(colors.menu_item(13, "Sum of total weight of all deliveries"))
        print(colors.menu_item(14, "Count Deliveries By Status(Optional)"))
        print(colors.menu_item(15, "Edit delivery"))
        print(colors.menu_exit(0, "Exit"))

        choice = input(colors.info("Choose an option: "))

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
            case "10":
                order_deliveries_menu()
            case "11":
                search_by_name_or_town_menu()
            case "12":
                average_weight_menu()
            case "13":
                sum_total_weight_menu()
            case "14":
                count_deliveries_menu()
            case "15":
                edit_delivery_menu()
            case "0":
                db.close_database()
                print(colors.success("Goodbye!"))
                is_running = False
            case _:
                print(colors.error("Invalid choice. Please try again."))


if __name__ == "__main__":
    main()