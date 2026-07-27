from datetime import datetime

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
        if value <= 0 or not isinstance(value, (int, float)):
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
        print(e)
        return False

    success = db.create_package(shipment)

    if success:
        print("Пратката е добавена успешно")

    return success

def show_all_deliveries(db):
    all_shipments = db.print_all()

    if not all_shipments:
        print("Няма пратки.")
        return

    for tracking_number, origin_city, destination_city, weight, current_status in all_shipments:
        print(f"{tracking_number} | {origin_city} -> {destination_city} | {weight}kg | {current_status}")

def search_by_tracking_number(db, tracking_number):

    shipment = db.print_by_tracking_num(tracking_number)

    if not shipment:
        print("Такава пратка не съществува")
        return

    print(shipment)

def change_status(db, tracking_number, new_status):

    db.update_state(tracking_number, new_status)

def show_history(db, tracking_number):

    shipment = db.print_status_history(tracking_number)

    if not shipment:
        print("Няма пратка с този номер")
    print(shipment)

def delete_package(db, tracking_number):

    db.delete_package(tracking_number)


