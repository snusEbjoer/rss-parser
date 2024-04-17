from bs4 import BeautifulSoup
import feedparser
import requests
import sqlite3

response = requests.get("https://volgograd-trv.ru/rss.xml") # получаем gеt запросом html новостей 

feed = feedparser.parse(response.text) # парсим текст
db_name = "sqlite.db"

def prepare(): # создаём в бд таблицы если их не существует
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    # Создаем таблицу News
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS News (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    category TEXT NOT NULL,
    author TEXT,
    full_text TEXT NOT NULL,
    pub_date TEXT NOT NULL
    );
    ''')
    # Сохраняем изменения и закрываем соединение
    connection.commit()
    connection.close()

def create_news(title, link, category, author, full_text, pub_date): # добавляем в бд новость
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO News(title, link, category, author, full_text, pub_date) VALUES (?,?,?,?,?,?);", (title, link, category, author,full_text, pub_date))
    connection.commit()
    connection.close()

def extract_text(p): # достаём текст из <p> тэгов исключая кнопки и пустые тэги
    text = ""
    for el in p:
        text += el.get_text()
    return text

def get_content():
    for entry in feed.entries[::-1]:
        content = entry["content"][0]["value"] 
        title = entry["title"]
        link = entry["link"]
        author = entry["author"]
        category = entry["category"]
        pub_date = entry["published"]
        
        soup = BeautifulSoup(content, "html.parser")
        p = soup.find_all("p")

        create_news(title, link, category, author, extract_text(p), pub_date)

def main():
    prepare()
    get_content()

main()