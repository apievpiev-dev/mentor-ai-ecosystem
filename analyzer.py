# analyzer.py
import matplotlib.pyplot as plt
from wb_api import get_sales

def plot_sales(days=30):
    sales = get_sales(days=days) or []
    if not sales:
        print("Нет данных по продажам")
        return

    data = {}
    for s in sales:
        date = s.get("date")
        data[date] = data.get(date, 0) + 1

    dates = sorted(data.keys())
    values = [data[d] for d in dates]

    plt.plot(dates, values, marker="o")
    plt.title("Продажи по дням")
    plt.xlabel("Дата")
    plt.ylabel("Количество продаж")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
