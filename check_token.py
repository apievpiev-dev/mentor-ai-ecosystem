import requests

# 🔑 Подставь сюда свой токен
TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwOTA0djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc3MzI4NDI5MSwiaWQiOiIwMTk5MzQyMi01YmM2LTdjZDgtYTVkNi1kNTMzZGIzYzcxYzciLCJpaWQiOjE4OTc5MjYxMSwib2lkIjo0MjM2MTIxLCJzIjoxMDczNzU3OTUwLCJzaWQiOiI3OGI3MDA2NS02MGM4LTQwMjQtYWU2MS0xNzdmOGFhZjg4MDAiLCJ0IjpmYWxzZSwidWlkIjoxODk3OTI2MTF9.UfGxwe93ynaKBPwM2Pk569jSxNNhCdayPd1FVY_FQhsv31kETloc_AXrV2mHTBNyq9vmLNq6bq2jGMWJu40iOA"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Набор эндпоинтов для проверки
ENDPOINTS = {
    "Карточки (content-api)": ("content-api.wildberries.ru", "/content/v2/get/cards/list", {
        "settings": {"cursor": {"limit": 1}}
    }),
    "Карточки (suppliers-api)": ("suppliers-api.wildberries.ru", "/content/v2/get/cards/list", {
        "settings": {"cursor": {"limit": 1}}
    }),
    "Заказы (statistics-api)": ("statistics-api.wildberries.ru", "/api/v1/supplier/orders", {
        "dateFrom": "2025-01-01", "dateTo": "2025-01-07"
    }),
    "Продажи (statistics-api)": ("statistics-api.wildberries.ru", "/api/v1/supplier/sales", {
        "dateFrom": "2025-01-01", "dateTo": "2025-01-07"
    }),
    "Остатки (statistics-api)": ("statistics-api.wildberries.ru", "/api/v1/supplier/stocks", {
        "dateFrom": "2020-01-01"
    }),
    "Баланс (statistics-api GET)": ("statistics-api.wildberries.ru", "/api/v1/supplier/balance", None),
}

def test_endpoint(name, host, path, payload):
    url = f"https://{host}{path}"
    try:
        if payload is None:  # GET-запрос
            r = requests.get(url, headers=HEADERS, timeout=15)
        else:  # POST-запрос
            r = requests.post(url, headers=HEADERS, json=payload, timeout=15)

        if r.status_code == 200:
            print(f"[✅ OK] {name} → доступен")
            return True
        elif r.status_code == 401:
            print(f"[⛔ AUTH] {name} → токен неверный или без прав")
        elif r.status_code == 403:
            print(f"[🚫 FORBIDDEN] {name} → токен не имеет доступа")
        elif r.status_code == 404:
            print(f"[❓ 404] {name} → эндпоинт не найден (возможно, устарел)")
        else:
            print(f"[⚠️ {r.status_code}] {name} → ошибка: {r.text[:100]}")
    except Exception as e:
        print(f"[ERR] {name} → {e}")
    return False

if __name__ == "__main__":
    print("🔎 Проверка токена WB API...\n")
    for name, (host, path, payload) in ENDPOINTS.items():
        test_endpoint(name, host, path, payload)
