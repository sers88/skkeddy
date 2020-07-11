import requests
import sqlite3
from datetime import datetime
import json
import time
import logging
import sys

def logger_basic(level, message, exits=True):#аргумент exits для выхода их программы
    "обработчик логов"
    logging.basicConfig(format=u'%(levelname)-4s [%(asctime)s] %(message)s',
                        level=logging.ERROR, filename=u'CodeNameSkeddyError.log')
    logging.log(level, message)
    if exits:
        sys.exit(0)

def read_file(file_path):
    "чтение текстового файла в одной функции"
    try:
        with open(file_path, 'r') as file:
            out_file = file.read()
        return out_file
    except IOError:
        logger_basic(40, ('Not found file:' +' ' + file_path))

def write_file(file_path, iteg):
    "запись в текстовый файл"
    try:
        with open(file_path, 'a') as file:
            file.write(iteg)
    except PermissionError:
        logger_basic(40, ('Permission error:' +' ' + file_path))

def get_orgs_dict():
    """таблица база код + название точки"""
    orgs = {}
    conn = sqlite3.connect(r'./orgsdb.db')
    cur = conn.cursor()
    cur.execute("SELECT ExternalId, FullName, Network, Phone FROM orgs")
    for line in cur:
        orgs[line[0]] = {}
        orgs[line[0]]['ExternalId'] = line[0]
        orgs[line[0]]['FullName'] = line[1]
        orgs[line[0]]['Network'] = line[2]
        orgs[line[0]]['Phone'] = line[3]
    return orgs

def get_orgs_dictKams():
    """таблица база камов + код точки"""
    kams = {}
    conn = sqlite3.connect(r'./orgsdb.db')
    cur = conn.cursor()
    cur.execute("SELECT ExternalId, kam FROM kams")
    for line in cur:
        kams[line[0]] = {}
        kams[line[0]]['ExternalId'] = line[0]
        kams[line[0]]['kam'] = line[1]
    return kams

def get_task_id(host, headers,page=1):
    """функция перебора заявок ?user_id=1304,5199,5196,517,1051,5197,2239,1240,5195,2190,3,1101,5,2399"""
    '''tickets = requests.get(host + 'tickets/?owner_list=1304,5199,5196,517,1051,5197,2239,1240,5195,2190,3,1101,5,2399'
                                      '&order_by=date_updated',
                               headers=headers).json()'''
    tickets = requests.get(host + 'tickets/?page={}&department_id=1,19&status_list=open'
                                      '&order_by=date_updated'.format(page),
                               headers=headers).json()
    task = list(dict.keys(tickets['data']))
    return task

def get_pages_id(host, headers):
    """func количество страниц по депортаментам"""
    tickets = requests.get(host + 'tickets/?department_id=1,19&status_list=open'
                                    '&order_by=date_updated',
                            headers=headers).json()
    pages_id = tickets['pagination']['total_pages']
    return pages_id


def get_department_id(ticket):
    """получи департамент"""
    depart = (ticket['data']['department_id'])
    return depart

def get_code_fileds(ticket):
    """найти элемент код точки"""
    value = ticket['data']['custom_fields']
    for elem in value:
        valuedict = (dict.items(elem))
        if ('id', 39) in valuedict:
            new = list(valuedict)
            return new

def get_task_fullname(ticket):
    """получи имя точки"""
    value = ticket['data']['custom_fields']
    for elem in value:
        valuedict = (dict.items(elem))
        if ('id', 40) in valuedict:
            new2 = list(valuedict)
            return new2

def get_fullname(orgs, code):
    """получи fullname для data"""
    try:
        return (orgs['{}'.format(code)]['FullName'])
    except KeyError:
        return (orgs['0']['FullName'])

def get_Network(orgs, code):
    """получи Network для data"""
    try:
        return (orgs['{}'.format(code)]['Network'])
    except KeyError:
        return (orgs['0']['Network'])

def get_orgs_phone(orgs, code):
    """получи телефон Организации из data"""
    try:
        return (orgs['{}'.format(code)]['Phone'])
    except:
        return (orgs['0']['Phone'])

def get_kam_data(kams, code):
    """получи Кама из data"""
    try:
        return (kams['{}'.format(code)]['kam'])
    except:
        return (kams['000001']['kam'])

def get_kam_in_task(ticket):
    """получи кама с сервера"""
    value = ticket['data']['custom_fields']
    for elem in value:
        valuedict = (dict.items(elem))
        if ('id', 41) in valuedict:
            new3 = list(valuedict)
            return new3

def get_kam_id(kam_data):
    if kam_data == 'Улецко Денис':
        return '203'
    elif kam_data == 'Стариков Алексей':
        return '374'
    elif kam_data == 'Репина Мария':
        return '205'
    elif kam_data == 'Смирнова Татьяна':
        return '395'
    elif kam_data == 'Прищепенко Ирина':
        return '375'
    elif kam_data == 'Мудракова Екатерина':
        return '204'
    elif kam_data == 'Молчанов Федор':
        return '50'
    elif kam_data == 'Малолыченко Дарья':
        return '374'
    elif kam_data == 'Карибджанян Наринэ':
        return '372'
    elif kam_data == 'Жирнов Сергей':
        return '48'
    elif kam_data == 'Гогашвили Тамара':
        return '50'
    elif kam_data == 'Волкова Алина':
        return '202'
    elif kam_data == 'Ахмерова Карина':
        return '395'
    elif kam_data == 'Аношкина Анастасия':
        return '374'
    elif kam_data == "НетКама":
        return '395'
    else:
        return "395"

def get_phone_in_task(ticket):
    """получи текущий телефон с сервера"""
    value = ticket['data']['custom_fields']
    for elem in value:
        valuedict = (dict.items(elem))
        if ('id', 63) in valuedict:
            new4 = list(valuedict)
            return new4

def update_task(field_name, name, network_name, host, task_id, headersJS):
    """обнови тикет название(сеть)"""
    if field_name == name:
        logging.info('Имя точки уже обновлено')
    else:
        data = {"custom_fields": {40: name, 84: network_name}}
        giveName = requests.put(host + 'tickets/{}'.format(task_id), headers=headersJS, data=json.dumps(data))
        logging.info('Задаче присвоено имя: {}'.format(name) + '\nЗадаче присвоена сеть: {}'.format(network_name))
        return giveName

def update_phone(phone_field, code_field, orgs_phone, orgs, host, task_id, headersJS):
    """обнови тетефон (контакт)"""
    if phone_field == '+7' or phone_field == '' or (phone_field == 'NULL' and code_field['field_value']
                                                    in orgs and orgs_phone != 'NULL'):
        data = {"custom_fields": {63: orgs_phone}}
        givePhone = requests.put(host + 'tickets/{}'.format(task_id), headers=headersJS, data=json.dumps(data))
        logging.info('Задаче присвоен номер телефона: {}'.format(orgs_phone))
        return givePhone
    else:
        logging.info('Телефон уже задан')

def update_kam(kam_field, code_field, kam_id, kam_data, orgs, host, task_id, headersJS):
    """метод для подставки кама точки"""
    if kam_field == '0' or (kam_field == '395' and (code_field['field_value'] != '0'
                                                    and code_field['field_value'] in orgs and kam_id != '395')):
        data = {"custom_fields": {41: '{}'.format(kam_id)}}
        givaKam = requests.put(host + 'tickets/{}'.format(task_id), headers=headersJS, data=json.dumps(data))
        logging.info("Кам точки назначен: {}".format(kam_data))
        return givaKam
    else:
        logging.info("КАМ уже существует")

#логирование
level = logging.INFO
format = '[%(asctime)s]: %(message)s'
handlers = [logging.FileHandler('CodeNameSkeddyLOG'), logging.StreamHandler()]
logging.basicConfig(level=level, format=format, handlers=handlers)
