import requests
from bs4 import BeautifulSoup as bs4
from time import sleep
import xlsxwriter
import sqlite3

#Создаем файлик екселя и страницу товары
book = xlsxwriter.Workbook('Одежда для девочек.xlsx')
page = book.add_worksheet("Товары")

row = 0
column = 0

#Задаем ширину колонок для 5ти столбиков (6 может быть неограниченное количество характеристик)
page.set_column('A:A', 10)
page.set_column('B:B', 30)
page.set_column('C:C', 10)
page.set_column('D:D', 15)
page.set_column('E:E', 10)
page.set_column('F:F', 40)

headers = {"user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320"}

for count_page in range (1, 7):
    sleep(3)
    url = f'https://malena.prom.ua/g21341349-odezhda-dlya-devochek/page_{count_page}' #получаем страницы по порядку

    response = requests.get(url, headers=headers)
    soup = bs4(response.text, 'html.parser')
    # Получили весь код страницы и ее распарсили

    card_item = soup.find_all('a', {'class':'b-centered-image b-product-line__image-wrapper'})
    # получаем список в котором находятся наши ссылки на товары
    for teg_a in card_item: # Перебираем этот список и получаем ссылки на каждый товар
        card_url = teg_a.get('href')
        # card_url = teg_a['href'] работает по аналогии с предыдущей строкой
        sleep(2)

        response = requests.get(card_url, headers=headers)
        sleep(3)
        soup = bs4(response.text, 'html.parser')
        # Получили весь код страницы с товаром и ее распарсили
        column = 0

        id_item = soup.find('span', {'class': 'b-product__sku'}).text  # получили код товара
        page.write(row, column, id_item)  # записываем код товара
        column += 1

        name_item = soup.find('h1', {'class': 'b-title b-product__name'}).text  # Название товара
        page.write(row, column , name_item) #название товара
        column += 1

        v_nalicii = soup.find('span', {'class': 'b-product__state b-product__state_type_available'}).text  # наличие
        page.write(row, column, v_nalicii)  # наличие
        column += 1

        selling_type = soup.find('span', {'class': 'b-product__selling-type'}).text  # оптом или в розницу
        page.write(row, column, selling_type)  # опт-розница
        column += 1

        price = soup.find('p', {'class': 'b-product__price'}).text  # цена
        page.write(row, column, price)  # цена
        column += 1

        description = soup.find('div', {'class': 'b-content__body b-user-content'}).get_text()  # описание (весь текст из блока)
        page.write(row, column, description)  # описание
        column += 1

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
            page.write(row, column, speci)
            column += 1
            page.write(row, column, meaning)
            column += 1

        # card_item = (id_item, name_item, v_nalicii, selling_type, price, description, specifications)

        row += 1


book.close()


