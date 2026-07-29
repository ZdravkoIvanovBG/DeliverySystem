import time
import random
from concurrent.futures.thread import ThreadPoolExecutor
from threading import Thread


def process_shipment(tracking_number):
    time.sleep(random.randint(1, 5))

    new_status = random.choice([
        'В процес на обработка',
        'Транспортира се',
        'Пристигнала в център',
        'Предадена на куриер',
    ])

    return tracking_number, new_status


def process_undelivered_shipments(tracking_numbers):
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(process_shipment, tracking_numbers)

    return list(results)


# Допълнителна задача - алтернатива на ThreadPoolExecutor
# Тук сами си управляваме нишките, вместо executor да го прави вместо нас
class ShipmentWorker(Thread):
    def __init__(self, tracking_number):
        Thread.__init__(self)
        self.tracking_number = tracking_number
        self.result = None

    # run() съдържа кода, който ще се изпълнява в отделната нишка
    def run(self):
        status = process_shipment(self.tracking_number)
        self.result = status


def process_undelivered_shipments_with_threads(tracking_numbers):
    workers_list = []

    # първо създаваме по един worker за всяка пратка
    for number in tracking_numbers:
        worker = ShipmentWorker(number)
        workers_list.append(worker)

    # start() пуска нишката да работи, без да чака да свърши
    for worker in workers_list:
        worker.start()

    # join() чака нишката да приключи, преди да продължим напред
    for worker in workers_list:
        worker.join()

    results = []
    for worker in workers_list:
        results.append(worker.result)

    return results