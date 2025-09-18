# main.py
from reports import build_report
from analyzer import plot_sales

if __name__ == "__main__":
    print("1. Отчёт CTR/STR")
    print("2. График продаж")

    choice = input("Выбери действие: ")

    if choice == "1":
        build_report(days=30, limit=10)
    elif choice == "2":
        plot_sales(days=30)
    else:
        print("Неизвестная команда")
