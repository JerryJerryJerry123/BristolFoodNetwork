from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import csv

from marketplace.models import Order, SubOrder


@login_required
def financial_report(request):
    if not request.user.is_staff:
        return HttpResponseForbidden("Not allowed")

    COMMISSION_RATE = Decimal("0.05")

    # -----------------------------
    # 1. DATE FILTERS (DATE-ONLY)
    # -----------------------------
    today = timezone.now().date()

    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    # Default: past 14 days
    if start_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    else:
        start_date = today - timedelta(days=14)

    if end_date_str:
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    else:
        end_date = today

    # Prevent future dates
    if end_date > today:
        end_date = today

    # -----------------------------
    # 2. SUBORDERS IN DATE RANGE
    # -----------------------------
    suborders = SubOrder.objects.filter(
        order__created_at__date__range=[start_date, end_date]
    ).exclude(status="cancelled")

    # Estimated revenue (pending + ready + delivered)
    estimated_suborders = suborders.filter(status__in=["pending", "ready", "delivered"])
    estimated_revenue = estimated_suborders.aggregate(total=Sum("subtotal"))["total"] or Decimal("0")
    estimated_commission = estimated_revenue * COMMISSION_RATE

    # Confirmed revenue (delivered only)
    confirmed_suborders = suborders.filter(status="delivered")
    confirmed_revenue = confirmed_suborders.aggregate(total=Sum("subtotal"))["total"] or Decimal("0")
    confirmed_commission = confirmed_revenue * COMMISSION_RATE

    # Distinct orders count
    num_orders = suborders.values("order").distinct().count()

    # -----------------------------
    # 3. YTD COMMISSION
    # -----------------------------
    ytd_start = datetime(end_date.year, 1, 1).date()

    ytd_suborders = SubOrder.objects.filter(
        order__created_at__date__range=[ytd_start, end_date],
        status="delivered"
    )

    ytd_total = ytd_suborders.aggregate(total=Sum("subtotal"))["total"] or Decimal("0")
    ytd_commission = ytd_total * COMMISSION_RATE

    # -----------------------------
    # 4. ORDER BREAKDOWN
    # -----------------------------
    orders = Order.objects.filter(
        created_at__date__range=[start_date, end_date]
    ).distinct()

    order_data = []
    for order in orders:
        suborders_list = []
        for sub in order.suborders.all():
            producer_payment = sub.subtotal * Decimal("0.95")
            suborders_list.append({
                "producer": sub.producer.username,
                "subtotal": sub.subtotal,
                "producer_payment": producer_payment,
                "delivery_date": sub.delivery_date,
                "status": sub.status,
            })

        order_data.append({
            "order": order,
            "total": order.total_amount,
            "commission": order.total_amount * COMMISSION_RATE,
            "suborders": suborders_list,
        })

    # -----------------------------
    # 5. CSV EXPORT
    # -----------------------------
    if request.GET.get("export") == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="financial_report.csv"'
        writer = csv.writer(response)

        writer.writerow([
            "Order ID", "Order Total", "Commission",
            "Producer", "SubOrder Total", "Producer Payment",
            "Delivery Date", "Status"
        ])

        for o in order_data:
            for s in o["suborders"]:
                writer.writerow([
                    o["order"].id,
                    o["total"],
                    o["commission"],
                    s["producer"],
                    s["subtotal"],
                    s["producer_payment"],
                    s["delivery_date"],
                    s["status"],
                ])

        return response

    # -----------------------------
    # 6. ALL-TIME TOTALS
    # -----------------------------
    all_time_suborders = SubOrder.objects.filter(status="delivered")
    all_time_total = all_time_suborders.aggregate(total=Sum("subtotal"))["total"] or Decimal("0")
    all_time_commission = all_time_total * COMMISSION_RATE

    # -----------------------------
    # 7. RENDER TEMPLATE
    # -----------------------------
    return render(request, "reports/financial_report.html", {
        "orders": order_data,
        "start_date": start_date,
        "end_date": end_date,
        "estimated_revenue": estimated_revenue,
        "estimated_commission": estimated_commission,
        "confirmed_revenue": confirmed_revenue,
        "confirmed_commission": confirmed_commission,
        "num_orders": num_orders,
        "ytd_commission": ytd_commission,
        "all_time_revenue": all_time_total,
        "all_time_commission": all_time_commission,
    })
