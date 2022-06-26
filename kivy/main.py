from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.lang import Builder

Builder.load_string('''
<Container>:
    padding: 30
    spacing: 30
    url: url
    button_text: button_text


    BoxLayout:
        orientation: 'vertical'

        Label:
            text: "Введите URL адрес сайта на Prom.ua (без последнего знака /): "
            font_size: 15
            size_hint: 1, 0.25


        TextInput:
            text: ''
            id: url
            multiline: False
            font_size: 15
            size_hint: 1, 0.75

    Button:
        text: 'Начать \nсканирование'
        id: button_text
        font_size: 20
        size_hint: 0.3, 1
        on_release:
            #указываем событие которое происходит при нажатии на кнопку
            root.parsing_go()
''')

import requests
import random
from time import sleep
from bs4 import BeautifulSoup as bs4
import sqlite3 as sql


# эта функция принимает один параметр - ссылку на карточку товара на пром юа и записывает в БД another_site.sqlite данные в 2 таблицы
def card_parser(card_href, url_site, group_title):
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320"}
    response = requests.get(card_href, headers=headers)
    sleep(random.randint(1, 5))
    soup = bs4(response.text, 'html.parser')  # Получили весь код страницы с товаром и ее распарсили
    # получили код товара ========================================
    try:
        id = soup.find('span', {'data-qaid': 'product_code'}).text  # получили код товара
    except:
        id = None
    # Название товара ============================================
    try:
        name = soup.find('span', {'data-qaid': 'product_name'}).text  # Название товара
    except:
        name = None
    # наличие ====================================================
    try:
        v_nalicii = soup.find('li', {'data-qaid': 'presence_data'}).text
    except:
        v_nalicii = None
    # цена =======================================================
    try:
        price = soup.find('span', {'data-qaid': 'product_price'}).text + " " + soup.find('span',
                                                                                         {'data-qaid': 'currency'}).text
    except AttributeError:
        price = soup.find('p', {'data-qaid': 'product_price'}).text
    except:
        price = None
    # Описание ===================================================
    try:
        description = soup.find('div',
                                {'data-qaid': 'product_description'}).get_text()  # описание (весь текст из блока)
    except:
        description = None
    # Фото товара ================================================
    # Характеристики =============================================
    specifications_soup = soup.find_all('td', {'class': 'b-product-info__cell'})  # суп из характеристик
    # дальше этот список нам нужно преобразовать , перебрать и опять преобразовать в понятный формат
    spisok = []  # создаем список в котором мы сохраним значения характеристик
    for i in specifications_soup:
        spisok.append((i.getText()).strip())
        # перебираем наши характеристики и обрезаем лишние пробелы и абзацы по обе стороны и добавляем все в список
        # записываем переменную характеристикики списком
    specifications = []
    for el in range(1, len(spisok) + 1,
                    2):  # берем наш список характеристик и перебираем его с помощи ренжа с шагом через один
        specification = [spisok[el - 1], spisok[el]]  # записываем характеристику и значение в тупл
        specifications.append(specification)  # и добавляем его в список характеристики
    # =================================================================================

    connection = sql.connect(
        f'{url_site}.sqlite')  # создаем или конектимся с базой данных (ее название может быть с расширением db или sqlite)
    curs = connection.cursor()  # c помощью курсора можно совршать действия связаные с базой данных которая находится в переменной конекшн

    # ================================================================
    # в табличку товары вносим айди, имя, наличие, цену и описание с помощью переменных
    descriptions_with_parametrs = (
        f'''INSERT INTO {group_title} (id, name, v_nalicii, price, description) VALUES(?, ?, ?, ?, ?);''')
    description_tuple = (id, name, v_nalicii, price, description)
    curs.execute(descriptions_with_parametrs, description_tuple)
    connection.commit()

    # ================================================================
    # в табличку характеристики вносим айди (чтобы можно было потом привязать к какому товару идут эти характеристики), название характеристики и ее значение
    for speci, meaning in specifications:
        specifications_with_parametrs = (
            f'''INSERT INTO {group_title}_specifications (id, specification, value) VALUES(?, ?, ?);''')
        specifications_tuple = (id, speci, meaning)
        curs.execute(specifications_with_parametrs, specifications_tuple)
        connection.commit()


# эта функция принимает ссылку на группу товаров на сайте и возвращает число - количество страниц по ссылке
def how_many_pages(href):
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320"}
    response = requests.get(href, headers=headers)
    sleep(random.randint(1, 5))
    soup = bs4(response.text, 'html.parser')  # Получаем суп из полученых категорий ссылки
    # находим значение последней страницы
    try:
        count_page = int(soup.find('span', {'class': 'b-pager__dotted-link'}).find_next_sibling().text)
        # Если на странице больше 3х страниц тогда берем значение последней страницы из блок после 3х точек
    except:
        try:
            count_page = int(soup.find('div', {'class': 'b-pager'}).find('a', {
                'class': 'b-pager__link b-pager__link_pos_last'}).find_previous_sibling().text)  # если 2 или 3 страницы - берем последнее значение в блоке див
        except:
            count_page = 1  # если одна - выдает ошибку , поэтому просто записываем 1
    return count_page


import requests
from bs4 import BeautifulSoup as bs4
from time import sleep
import random
import sqlite3 as sql


# Задаем параметры ширины и высоты для нашего приложения
Window.size = (720, 300)

class Container(BoxLayout):
    button_text = ObjectProperty()
    url = ObjectProperty()
    process = 'Processing ...'

    def parsing_go(self):
        self.button_text.text = self.process
        url = self.url.text


        headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.188 Safari/537.36 CrKey/1.54.250320"}

        # ===============================================
        # Главная страница
        # ===============================================

        # 'https://autoklan.com.ua'
        product_list = url + '/product_list'
        response = requests.get(product_list, headers=headers)
        soup = bs4(response.text, 'html.parser')
        # Получили весь код страницы товаров и услуг и сделали из нее суп

        # Получаем список групп товаров
        groups_item = soup.find_all('li', {'class': 'cs-product-groups-gallery__item'})

        # Из этого списка нужно взять все ссылки и записать их в свой список
        href_groups = []
        for block in groups_item:
            href_a = block.find_all('a')
            for block_a in href_a:
                href = block_a.get('href')
                # одна группа товаров содержит 2 ссылки и несколько тегов а без ссылок , поэтому проверяем чтобы ссылка была и если она есть - берем первую ссылку
                if href != None:
                    # делаем ловец для ссылок который позволяет не сломать нашу программу если ссылка будет полная или относительная , это значительно замедляет нашу программу из за задержки слип от 1 до 5ти секунд, но зато нас точно не забанят (если сильно напрягает скорость работы - можно функции слип закоментировать)
                    try:
                        response = requests.get(href, headers=headers)
                        sleep(random.randint(1, 5))
                        href_groups.append(href)
                        break
                    except requests.exceptions.MissingSchema:
                        response = requests.get(url + href, headers=headers)
                        sleep(random.randint(1, 5))
                        href_groups.append(url + href)
                        break
        # вконце мы получаем список с ссылками на каждую группу товаров на сайте

        # ============================================
        # Группы товаров
        # ============================================

        # дальше большинство сайтов имеет еще и подгруппы , но и есть такие что имеют сразу список товаров
        for href in href_groups:
            response = requests.get(href, headers=headers)
            sleep(random.randint(1, 5))
            soup = bs4(response.text, 'html.parser')  # Получаем суп из полученой категории товаров
            title = (soup.find('h1', {'class': 'cs-title'}).text.replace('-', '_').replace('+', '_').replace(' ',
                                                                                                             '_').replace(
                ',', '_').replace('.', '_').replace('(', '').replace(')', '').replace('/', '').replace("'", ''))
            # получаем название категории товаров и записываем ее в переменную тайтл чтобы потом создать таблицу в БД с названием этой переменной

            site = url.replace('https://', '').replace('.com', '').replace('.prom', '').replace('.net', '').replace(
                '.ua',
                '')  # Делаем так чтобы название нашей таблицы было таким же как название домена сайта (если домен будет еще какой-то дополнительно - добавить реплейсы или переделать систему парсинга ссылки)
            connection = sql.connect(
                f'{site}.sqlite')  # создаем или конектимся с базой данных (ее название может быть с расширением db или sqlite)
            curs = connection.cursor()  # c помощью курсора можно совршать действия связаные с базой данных которая находится в переменной конекшн

            # Создаем табличку товаров в базе данных
            try:
                curs.execute(
                    f'''CREATE TABLE {title} (id VARCHAR , name TEXT , v_nalicii TEXT , price VARCHAR , description TEXT )''')
                connection.commit()
            except:
                pass  # если табличка уже есть - не создаем
            # Создаем табличку с характеристиками и называем ее как название группы товаров с добавлением слова характеристики
            try:
                curs.execute(f'''CREATE TABLE {title}_specifications (id VARCHAR , specification TEXT , value TEXT)''')
                connection.commit()
            except:
                pass  # если табличка уже есть - не создаем

            # дальше воспользуемся функцией для определения кол-ва страниц в текущей группе товаров
            last_page = how_many_pages(href) + 1
            for count_page in range(1, last_page):
                main_page = f'{href}/page_{count_page}'  # получаем страницы по порядку и записываем в переменную текущая страница по порядку
                response = requests.get(main_page, headers=headers)
                soup = bs4(response.text, 'html.parser')
                sleep(random.randint(1, 5))
                # Получили весь код страницы и ее распарсили

                card_li = soup.find_all('li', {'data-tg-chain': '{"view_type": "preview"}'})
                # находим список всех товаров и нужно будет вытянуть ссылку на каждый товар по отдельности

                for a in card_li:
                    all_a = a.find_all('a')
                    # Нашли все теги а

                    for href_a in all_a:
                        card_href = href_a.get('href')
                        # вытянули из них все ссылку на каждый товар

                        # =========================================
                        # Товар
                        # =========================================

                        if card_href != None:
                            card_parser(card_href, site,
                                        title)  # исспользуем функцию которую я создал для парсинга ссылки любой товар на проме
                            break

class DuckyApp(App):
    def build(self):
        return Container()

if __name__ == '__main__':
    DuckyApp().run()