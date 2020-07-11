import requests
import sqlite3
from datetime import datetime
import json
import time
import logging
import DefSkeddy as ds
import sys

base = ds.read_file('./base')

host = 'https://plazius.helpdeskeddy.com/api/v2/'
headers = {
    'Authorization': 'Basic %s' % base,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cache-Control': 'no-cache',
}

headersJS = {
    'Authorization': 'Basic %s' % base,
    'Content-Type': 'application/json',
    'Cache-Control': 'no-cache',
}
NAME_FILE = 'full_task_bd.txt'
#логирование
level = logging.INFO
format = '[%(asctime)s]: %(message)s'
handlers = [logging.FileHandler('CodeNameSkeddyLOG'), logging.StreamHandler()]
logging.basicConfig(level=level, format=format, handlers=handlers)

#прочитай таблицу
orgs = ds.get_orgs_dict()
kams = ds.get_orgs_dictKams()

#айди заявки
full_task = list()
pages_id = ds.get_pages_id(host, headers)#количество страниц
if pages_id > 1:
    for page in range(1,pages_id+1):
        full_task.extend(ds.get_task_id(host, headers, page))
else:
    full_task = ds.get_task_id(host, headers)


file_task_bd = list(ds.read_file(NAME_FILE).split())#получение обработаных заявок из файла
for bd_task in file_task_bd:
    for y,id_task in enumerate(full_task):
        if id_task == bd_task:
            full_task.pop(y)
num_task = len(full_task)
if num_task == 0:
    sys.exit(0)
else:
    ds.write_file(NAME_FILE, '\n')#добавление новой строки в файл
ds.write_file(NAME_FILE, '\n'.join(full_task))#запись новых заявок в бд файл

while True:
    task_id = full_task[num_task - 1]
    num_task = num_task - 1
    logging.info("Номер заявки: {}".format(task_id))
#для перебора data
    ticket = requests.get(host + 'tickets/{}'.format(task_id), headers=headers).json()
    depart_id = ds.get_department_id(ticket)
    logging.info("Индификатор департамента: {}".format(depart_id))

    if depart_id == 1 or depart_id == 19:
        code_field = dict(ds.get_code_fileds(ticket))
#код для сравнения в бд
        code = str(code_field['field_value'])
        try:
            Name_field = (dict(ds.get_task_fullname(ticket)))
        except TypeError:
            Name_field = {'field_value': 'Точка не задана'}
        field_name = (Name_field['field_value'])
        name = ds.get_fullname(orgs, code)
        network_name = ds.get_Network(orgs, code)
        orgs_phone = ds.get_orgs_phone(orgs, code)
        kam_data = ds.get_kam_data(kams, code)
        try:
            kam_field = str(dict(ds.get_kam_in_task(ticket))['field_value']['id'])
        except:
            kam_field = 395
        kam_id = ds.get_kam_id(kam_data)
        try:
            phone_field = str(dict(ds.get_phone_in_task(ticket))['field_value'])
        except TypeError:
            phone_field = '+7'

#запуск апдейтов
        ds.update_task(field_name, name, network_name, host, task_id, headersJS)
        ds.update_phone(phone_field, code_field, orgs_phone, orgs, host, task_id, headersJS)
        ds.update_kam(kam_field, code_field, kam_id, kam_data, orgs, host, task_id, headersJS)

    else:
        logging.info("в данной задаче нет такого параметра")
    time.sleep(2)
    if num_task == 0 :
        break
