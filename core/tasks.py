from celery import shared_task
import time


@shared_task
def add(x, y):
    """
    A simple addition async task that simulates time-consuming operations
    """
    # Simulate 5 seconds of processing time
    time.sleep(5)
    return x + y
