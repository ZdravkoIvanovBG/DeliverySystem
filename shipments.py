from datetime import datetime

import colors  # добавено: цветен изход


class Shipment:
    ALLOWED_STATUSES = [
        'Регистрирана',
        'Приета в офис',
        'В процес на обработка',
        'Транспортира се',
        'Пристигнала в център',
        'Предадена на куриер',
        'Доставена',
        'Неуспешна доставка'
    ]

    def __init__(self, tracking_number, sender_name, recipient_name, origin_city, destination_city, weight):
        self.tracking_number = tracking_number
        self.sender_name = sender_name
        self.recipient_name = recipient_name
        self.origin_city = origin_city
        self.destination_city = destination_city
        self.weight = weight
        self.created_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.current_status = "Регистрирана"
        self.status_history = f"{self.created_at} - {self.current_status}"

    @property
    def tracking_number(self):
        return self.__tracking_number

    @tracking_number.setter
    def tracking_number(self, value):
        if value.strip() == "":
            raise ValueError("Tracking number cannot be empty")
        self.__tracking_number = value

    @property
    def sender_name(self):
        return self.__sender_name

    @sender_name.setter
    def sender_name(self, value):
        if value.strip() == "":
            raise ValueError("Sender name cannot be empty")
        self.__sender_name = value

    @property
    def recipient_name(self):
        return self.__recipient_name

    @recipient_name.setter
    def recipient_name(self, value):
        if value.strip() == "":
            raise ValueError("Recipient name cannot be empty")
        self.__recipient_name = value

    @property
    def origin_city(self):
        return self.__origin_city

    @origin_city.setter
    def origin_city(self, value):
        if value.strip() == "":
            raise ValueError("Origin city cannot be empty")
        self.__origin_city = value

    @property
    def destination_city(self):
        return self.__destination_city

    @destination_city.setter
    def destination_city(self, value):
        if value.strip() == "":
            raise ValueError("Destination city cannot be empty")
        self.__destination_city = value

    @property
    def weight(self):
        return self.__weight

    @weight.setter
    def weight(self, value):
        if not isinstance(value, (int, float)) or value <= 0:  # поправено: първо проверка на типа
            raise ValueError("Weight must be greater than 0 and be a number")
        self.__weight = value

    def change_status(self, new_status):
        if new_status not in self.ALLOWED_STATUSES:
            raise ValueError("Invalid status")

        time_of_change = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        self.current_status = new_status
        self.status_history += f"\n{time_of_change} - {new_status}"


def add_delivery(db, tracking_number, sender_name, recipient_name, origin_city, destination_city, weight):
    try:
        shipment = Shipment(tracking_number, sender_name, recipient_name, origin_city, destination_city, weight)
    except ValueError as e:
        print(colors.error(str(e)))
        return False

    success = db.create_package(shipment)

    if success:
        print(colors.success("The delivery was added successfully!"))

    return success


def show_all_deliveries(db):
    all_shipments = db.print_all()
    _print_shipment_rows(all_shipments)


def search_by_tracking_number(db, tracking_number):
    shipment = db.print_by_tracking_num(tracking_number)

    if not shipment:
        print(colors.warning("There's no delivery with the given tracking number"))
        return

    for tracking_number, sender_name, recipient_name, origin_city, destination_city, weight, current_status in shipment:
        print(f"{tracking_number} | {sender_name} | {recipient_name} | {origin_city} -> {destination_city} | {weight}kg | {current_status}")

def change_status(db, tracking_number, new_status):
    if new_status not in Shipment.ALLOWED_STATUSES:  # поправено: валидация на статуса
        print(colors.error("Невалиден статус. Изберете от предварително зададения списък."))
        return False

    result = db.update_state(tracking_number, new_status)

    if not result:
        print(colors.warning("There's no delivery with the given tracking number"))
        return False

    print(colors.success("The status was changed successfully!"))
    return True

def show_history(db, tracking_number):
    shipment = db.print_status_history(tracking_number)

    if not shipment:
        print(colors.warning("There's no delivery with the given tracking number"))
        return
    print(shipment)


def delete_package(db, tracking_number):
    db.delete_package(tracking_number)


def filter_shipments(db, status=None, city=None, min_weight=None):
    """Допълнителна задача (ново): филтриране по статус, град и/или минимално тегло."""
    results = db.filter_shipments(status=status, city=city, min_weight=min_weight)
    _print_shipment_rows(results)


def _print_shipment_rows(rows):
    if not rows:
        print(colors.warning("No deliveries found matching the criteria."))
        return

    for tracking_number, origin_city, destination_city, weight, current_status in rows:
        print(f"{tracking_number} | {origin_city} -> {destination_city} | {weight}kg | {current_status}")

def order_deliveries(db, sort_by, direction):
    shipments = db.order_deliveries_by_weight_date_city(sort_by, direction)

    if not shipments:
        print(colors.warning("No deliveries found matching the criteria."))
    else:
        for tracking_number, origin_city, destination_city, weight, current_status, created_at in shipments:
            print(f"{tracking_number} | {origin_city} -> {destination_city} | {weight}kg | {current_status} | {created_at}")

def search_by_name_or_town(db, search_term):
    deliveries = db.search_by_name_or_town(search_term)

    if not deliveries:
        print(colors.warning("No deliveries found matching the criteria."))
    else:
        for tracking_number, sender_name, origin_city, destination_city, weight, current_status in deliveries:
            print(f"{tracking_number} | {sender_name} | {origin_city} -> {destination_city} | {weight}kg | {current_status}")

def average_weight(db):
    avg_weight = db.average_weight()

    print(f"Average weight: {avg_weight}kg")

def sum_total_weight(db):
    total_weight = db.sum_total_weight()

    print(f"Total weight: {total_weight}kg")

def count_deliveries(db, status):
    count = db.count_deliveries(status)

    print(f"Number of deliveries: {count}")

def edit_delivery(db, tracking_number, field, new_value):
    success = db.edit_delivery_field(tracking_number, field, new_value)

    if not success:
        print(colors.warning("There's no delivery with the given tracking number"))
    else:
        print(colors.success(f"The {field} was updated successfully!"))