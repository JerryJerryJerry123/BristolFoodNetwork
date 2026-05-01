from django.core.management.base import BaseCommand
from django.utils import timezone
from marketplace.models import SubOrder
from marketplace.services.delivery_simulator import attempt_delivery


class Command(BaseCommand):
    help = "Automatically attempts delivery for today's ready suborders"

    def handle(self, *args, **kwargs):
        today = timezone.now().date()

        suborders = SubOrder.objects.filter(
            status="ready",
            delivery_date=today
        )

        self.stdout.write(f"Attempting deliveries for {suborders.count()} suborders")

        for sub in suborders:
            attempt_delivery(sub)
            self.stdout.write(f"Processed SubOrder {sub.id}")