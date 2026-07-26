import time
import random
from concurrent.futures.thread import ThreadPoolExecutor


def process_shipment(tracking_number):
    time.sleep(random.randint(1, 5))

    new_status = random.choice([
        'В процес на обработка',
        'Транспортира се',
        'Пристигнала в център',
        'Предаде на куриер',
    ])

    return tracking_number, new_status

def process_undelivered_shipments(tracking_numbers):
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(process_shipment, tracking_numbers)

    return list(results)