import requests
import pandas as pd

# 🔑 Подставь сюда свой реальный API ключ Wildberries
API_KEY = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjUwOTA0djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc3MzI4NDI5MSwiaWQiOiIwMTk5MzQyMi01YmM2LTdjZDgtYTVkNi1kNTMzZGIzYzcxYzciLCJpaWQiOjE4OTc5MjYxMSwib2lkIjo0MjM2MTIxLCJzIjoxMDczNzU3OTUwLCJzaWQiOiI3OGI3MDA2NS02MGM4LTQwMjQtYWU2MS0xNzdmOGFhZjg4MDAiLCJ0IjpmYWxzZSwidWlkIjoxODk3OTI2MTF9.UfGxwe93ynaKBPwM2Pk569jSxNNhCdayPd1FVY_FQhsv31kETloc_AXrV2mHTBNyq9vmLNq6bq2jGMWJu40iOA"

# URL для получения карточек
url = "https://suppliers-api.wildberries.ru/content/v1/cards/filter"

# Заголовки авторизации
headers = {
    "Authorization": API_KEY,
    "Content-Type": "application/json"
}

# Запрос (limit можно увеличить до 1000)
payload = {
    "settings": {
        "cursor": {"limit": 50}
    }
}

# Отправляем запрос
response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    data = response.json()
    cards = data.get("data", {}).get("cards", [])

    articuls = []
    for card in cards:
        articuls.append({
            "nmID": card.get("nmID"),
            "title": card.get("title"),
            "supplierArticle": card.get("supplierArticle")
        })

    df = pd.DataFrame(articuls)
    print(df)
else:
    print("Ошибка:", response.status_code, response.text)
