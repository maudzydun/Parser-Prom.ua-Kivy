# import sqlite3  as sql


# connection = sql.connect('another_site.sqlite') #создаем или конектимся с базой данных (ее название может быть с расширением db или sqlite)
# curs = connection.cursor() #c помощью курсора можно совршать действия связаные с базой данных которая находится в переменной конекшн

import requests
from bs4 import BeautifulSoup as bs4

headers = {"user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320"}

for count_page in range (1, 3):

    url = f'https://extreme-market.com.ua/g95212779-smartfony-telefony/page_{count_page}' #получаем страницы по порядку
    response = requests.get(url, headers=headers)
    soup = bs4(response.text, 'html.parser')