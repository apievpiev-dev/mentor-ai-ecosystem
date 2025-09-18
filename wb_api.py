# wb_api.py
import requests
import socket
from datetime import datetime, timedelta
from config import HEADERS

CONTENT_HOST = "content-api.wildberries.ru"
STAT_HOST = "statistics-api.wildberries.ru"

def check_dns(host):
    try:
        socket.gethostbyname(host)
        return True
    except socket.gaierror:
        return False

def request_post(host, path, payload=None):
    if not check_dns(host):
        return None
    url = f"https://{host}{path}"
    try:
        r = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERR] {url}: {e}")
        return None

def request_get(host, path, params=None):
    if not check_dns(host):
        return None
    url = f"https://{host}{path}"
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERR] {url}: {e}")
        return None

# --- Контент ---
def get_cards(limit=10):
    payload = {"settings": {"cursor": {"limit": limit}}}
    return request_post(CONTENT_HOST, "/content/v2/get/cards/list", payload)

# --- Статистика ---
def get_orders(days=7):
    date_to = datetime.today().date()
    date_from = date_to - timedelta(days=days)
    return request_get(STAT_HOST, "/api/v1/supplier/orders",
                       {"dateFrom": str(date_from), "dateTo": str(date_to)})

def get_sales(days=7):
    date_to = datetime.today().date()
    date_from = date_to - timedelta(days=days)
    return request_get(STAT_HOST, "/api/v1/supplier/sales",
                       {"dateFrom": str(date_from), "dateTo": str(date_to)})

def get_stocks():
    return request_get(STAT_HOST, "/api/v1/supplier/stocks",
                       {"dateFrom": "2020-01-01"})
