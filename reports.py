# reports.py
from wb_api import get_cards, get_orders, get_sales
from tabulate import tabulate

def build_report(days=7, limit=5):
    cards = get_cards(limit=limit)
    orders = get_orders(days=days) or []
    sales = get_sales(days=days) or []

    orders_by_nm = {}
    for o in orders:
        nmId = o.get("nmId")
        if nmId:
            orders_by_nm[nmId] = orders_by_nm.get(nmId, 0) + 1

    sales_by_nm = {}
    for s in sales:
        nmId = s.get("nmId")
        if nmId:
            sales_by_nm[nmId] = sales_by_nm.get(nmId, 0) + 1

    table = []
    for card in cards.get("cards", []):
        nmId = card["nmID"]
        title = card["title"]
        views = 1000  # заглушка для показов
        o = orders_by_nm.get(nmId, 0)
        s = sales_by_nm.get(nmId, 0)

        ctr = round(o / views * 100, 2) if views else 0
        str_val = round(s / o * 100, 2) if o else 0

        table.append([nmId, title[:30], views, o, s, f"{ctr}%", f"{str_val}%"])

    print(tabulate(table, headers=["nmID", "Название", "Показы", "Заказы", "Выкупы", "CTR", "STR"]))
