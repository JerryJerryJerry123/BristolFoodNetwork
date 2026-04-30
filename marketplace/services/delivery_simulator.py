import random
from datetime import timedelta 
from django.utils import timezone

def attempt_delivery(suborder):
    """
    80% success rate delivery simulation
    """
    success = random.random() < 0.8

    if success:
        suborder.status = "delivered"
    else:
        suborder.status = "failed"
        suborder.delivery_date = suborder.delivery_date + timedelta(days=1)

    suborder.save()
    return success