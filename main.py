import os
import requests
import smtplib
import requests_cache
from dotenv import load_dotenv

requests_cache.install_cache("cache", expiry_after=300)
load_dotenv()

stock_price_api_key = os.getenv("STOCK_PRICE_API_KEY")
news_api_key = os.getenv("NEWS_API_KEY")
my_email = os.getenv("MY_EMAIL")
my_password = os.getenv("MY_PASSWORD")

stock_price_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": "TSLA",
    "outputsize": "compact",
    "datatype": "json",
    "apikey": stock_price_api_key,
}

response = requests.get("https://www.alphavantage.co/query", params=stock_price_params)
response.raise_for_status()
data = response.json()["Time Series (Daily)"]
last_two_days = [value for key, value in data.items()][:2]
closing_price_of_yesterday = float(last_two_days[0]["4. close"])
closing_price_of_day_before_yesterday = float(last_two_days[1]["4. close"])

fluctuation = round(closing_price_of_yesterday - closing_price_of_day_before_yesterday)
fluctuation_percentage = round((fluctuation / closing_price_of_day_before_yesterday) * 100)
signal = "🔺" if fluctuation_percentage > 0 else "🔻"

news_params = {
    "apiKey": news_api_key,
    "q": "TSLA",
    "language": "en",
    "sortBy": "publishedAt",
    "pageSize": 1,
}

response = requests.get("https://newsapi.org/v2/everything", params=news_params)
response.raise_for_status()
data = response.json()
latest_article = data["articles"][0]
article_title = latest_article["title"]
article_description = latest_article["description"]
article_url = latest_article["url"]

with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
    connection.starttls()
    connection.login(user=my_email, password=my_password)
    connection.sendmail(
        from_addr=my_email,
        to_addrs="armaanjamadarx@gmail.com",
        msg=f"Subject: TSLA {signal} by {fluctuation_percentage}%"
        f"\n\n{article_title}\n{article_description}\nRead more...\n{article_url}".encode(),
    )
