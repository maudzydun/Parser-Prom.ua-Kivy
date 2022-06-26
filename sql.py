import sqlite3 as sql

connection = sql.connect('xls.db') #создаем или конектимся с базой данных (ее название может быть с расширением db или sqlite)
curs = connection.cursor() #c помощью курсора можно совршать действия связаные с базой данных которая находится в переменной конекшн

# Создаем табличку в базе данных
try:
    curs.execute('''CREATE TABLE all_items(id varchar, name varchar, v_nalicii varchar, selling_type varchar, price varchar, description varchar)''')
    connection.commit()
except:
    pass #если табличка уже есть - не создаем

id = input ('')
name = input ('')
v_nalicii = input ('')
selling_type = input ('')
price = input ('')
description = input ('')


# Добавляем эти значения в нашу табличку в базе данных
curs.execute("INSERT INTO all_items (id, name, v_nalicii, selling_type, price, description) VALUES('%s', '%s', '%s', '%s', '%s', '%s')"%(id, name, v_nalicii, selling_type, price, description))
connection.commit()

# получаем все данные из таблички 
curs.execute("SELECT * FROM all_items")

# записываем в переменную ров ряд , при следующем вызове этой функции записывается уже следующий ряд
row = curs.fetchone()

while row is not None:
    print ('ID:', row[0], "name:", row[1], 'price:', row[4])
    row = curs.fetchone() #Следующий ряд

# если к базе данных подключились - нужно от нее и отключиться 
curs.close() #закрываем сначала курсор
connection.close() #и так же закрываем наше соединение
