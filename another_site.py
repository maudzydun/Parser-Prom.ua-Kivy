import requests
from bs4 import BeautifulSoup as bs4
from time import sleep
import sqlite3  as sql
import random
from parser_1 import card_parser

connection = sql.connect('another_site.sqlite') #создаем или конектимся с базой данных (ее название может быть с расширением db или sqlite)
curs = connection.cursor() #c помощью курсора можно совршать действия связаные с базой данных которая находится в переменной конекшн

# Создаем табличку в базе данных
try:
    curs.execute('''CREATE TABLE goods(id VARCHAR , name TEXT , v_nalicii TEXT , price VARCHAR , description TEXT )''')
    connection.commit()
except:
    pass #если табличка уже есть - не создаем

try:
    curs.execute('''CREATE TABLE specifications(id VARCHAR , specification TEXT , value TEXT )''') # создаем Таблицу в которую мы сохраним значения характеристик
    connection.commit()
except:
    pass #если табличка уже есть - не создаем


headers = {"user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320"}

for count_page in range (1, 3):
    sleep(random.randint(1, 5))
    url = f'https://extreme-market.com.ua/g95212779-smartfony-telefony/page_{count_page}' #получаем страницы по порядку
    response = requests.get(url, headers=headers)
    soup = bs4(response.text, 'html.parser')
    # Получили весь код страницы и ее распарсили
    
    card_li = soup.find_all('li', {'data-tg-chain':'{"view_type": "preview"}'})
    #находим список всех товаров и нужно будет вытянуть ссылку на каждый товар по отдельности
    
    for a in card_li:
        all_a = a.find_all('a')
        for href_a in all_a:
            card_href = href_a.get('href')

            if card_href != None:
                card_parser(card_href) #исспользуем функцию которую я создал для парсинга ссылки любой товар на проме
                break


    # получаем список в котором находятся наши ссылки на товары
    for teg_a in card_li: # Перебираем этот список и получаем ссылки на каждый товар
        card_url = teg_a.get('href')
        print(card_url)
        
        response = requests.get(card_url, headers=headers)
        sleep(3)
        soup = bs4(response.text, 'html.parser')
        # Получили весь код страницы с товаром и ее распарсили
        id = soup.find('span', {'data-qaid': 'product_code'}).text  # получили код товара
        print(id)
        name = soup.find('span', {'data-qaid': 'product_name'}).text  # Название товара
        print(name)
        v_nalicii = soup.find('li', {'data-qaid': 'presence_data'}).text  # наличие
        print(v_nalicii)

        try:
            price = soup.find('span', {'data-qaid': 'product_price'}).text +" "+ soup.find('span', {'data-qaid': 'currency'}).text # цена
            # print(price)
        except:
            price = (None)

        description = soup.find('div', {'data-qaid': 'product_description'}).get_text()  # описание (весь текст из блока)
        # print(description)
        # print(id, name, v_nalicii, price, description)
        # Добавляем эти значения в нашу табличку в базе данных
        curs.execute('''INSERT INTO goods (id, name, v_nalicii, price, description) VALUES('%s', '%s', '%s', '%s', "%s")'''%(id, name, v_nalicii, price, description))
        connection.commit()

        specifications_soup = soup.find_all('td', {'class': 'b-product-info__cell'})  # характеристики списком
        # дальше этот список нам нужно преобразовать , перебрать и опять преобразовать в понятный формат

        spisok = []  # создаем список в котором мы сохраним значения характеристик 
        for i in specifications_soup:
            spisok.append((i.getText()).strip())
            # перебираем наши характеристики и обрезаем лишние пробелы и абзацы по обе стороны и добавляем все в список
        # записываем переменную характеристикики списком
        specifications = []
        for el in range(1, len(spisok) + 1,2):  # берем наш список характеристик и перебираем его с помощи ренжа с шагом через один
            specification = [spisok[el - 1], spisok[el]]  # записываем характеристику и значение в тупл
            specifications.append(specification)  # и добавляем его в список характеристики
        # дальше нам нужно сделать так чтобы название характеристики было в одном поле а в следующем его значение
        for speci, meaning in specifications:
            curs.execute('''INSERT INTO specifications (id, specification, value) VALUES('%s', "%s", "%s")'''%(id, speci, meaning))
            connection.commit()
            
        