from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import csv

from marketplace.models import Order

@login_required
def financial_report(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    # --- Step 1: date filters ---
    end_date = timezone.now()
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if start_date_str:
        start_date = timezone.datetime.strptime(start_date_str, "%Y-%m-%d")
        start_date = timezone.make_aware(start_date)
    else:
        start_date = end_date - timedelta(days=14)

    if end_date_str:
        end_date = timezone.datetime.strptime(end_date_str, "%Y-%m-%d")
        end_date = timezone.make_aware(end_date)

    # Filter orders in period
    orders = Order.objects.filter(
        created_at__range=[start_date, end_date],
        total_amount__gt=Decimal('0')
                                  )

    # --- Step 2: summary calculations ---
    total_value = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
    total_commission = total_value * Decimal("0.05")
    num_orders = orders.count()

    # --- Step 3: YTD commission ---
    ytd_start = timezone.datetime(end_date.year, 1, 1)
    ytd_start = timezone.make_aware(ytd_start)
    ytd_orders = Order.objects.filter(created_at__gte=ytd_start, created_at__lte=end_date, total_amount__gt=Decimal('0'))
    ytd_total_value = ytd_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
    ytd_commission = ytd_total_value * Decimal("0.05")

    # --- Step 4: breakdown per order / suborder ---
    order_data = []
    for order in orders:
        suborders_list = []
        for sub in order.suborders.all():
            producer_payment = sub.total * Decimal("0.95")
            suborders_list.append({
                'producer': sub.producer.username,
                'subtotal': sub.total,
                'producer_payment': producer_payment,
                'delivery_date': sub.delivery_date,
            })
        order_data.append({
            'order': order,
            'total': order.total_amount,
            'commission': order.total_amount * Decimal("0.05"),
            'suborders': suborders_list,
        })

    # --- Step 5: CSV export ---
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="financial_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Order Total', 'Commission', 'Producer', 'SubOrder Total', 'Producer Payment', 'Delivery Date'])
        for o in order_data:
            for s in o['suborders']:
                writer.writerow([
                    o['order'].id,
                    o['total'],
                    o['commission'],
                    s['producer'],
                    s['subtotal'],
                    s['producer_payment'],
                    s['delivery_date'],
                ])
        return response

    # --- Step 6: render HTML ---
    return render(request, "reports/financial_report.html", {
        'orders': order_data,
        'total_value': total_value,
        'total_commission': total_commission,
        'num_orders': num_orders,
        'ytd_commission': ytd_commission,
        'start_date': start_date,
        'end_date': end_date,
    })