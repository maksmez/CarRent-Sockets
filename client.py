import datetime
import hashlib
import json
import socket
from termcolor import colored, cprint

client_socket = socket.socket()  # создаем сокет

car_values_list = {
    'Transmission': ['Механическая', 'Автоматическая'],
    'Engine': ['Бензиновый', 'Дизельный'],
    'Car_type': ['Седан', 'Кроссовер', 'Универсал', 'Хэтчбек', 'Купе', 'Микро'],
    'Drive': ['Полный', 'Задний', 'Передний'],
    'Wheel_drive': ['Правый', 'Левый']
}

fields_dict = {
    'cars': {
        'CompanyID': 'Id компании',
        'Location':  'Адрес компании',
        'Photos': 'Пути к фотографиям',
        'RentCondition': 'Условия аренды',
        'Header': 'Заголовок',
        'Driver': 'Есть ли водитель',
        'CategoryID': 'ID категории',
        'CategoryVU': 'Название категории ВУ',
        'FixedRate': 'Фиксированная комиссия',
        'Percent': 'Процент комиссии',
        'Brand_and_name': 'Марка и название',
        'Transmission': 'Трансмиссия',
        'Engine': 'Двигатель',
        'Car_type': 'Тип кузова',
        'Drive': 'Привод',
        'Wheel_drive': 'Положение руля',
        'Year': 'Год выпуска',
        'Power': 'Мощность',
        'Price': 'Стоимость'
    },
    'orders': {
        'DateStartContract': 'Дата начала аренды',
        'DateEndContract': 'Дата окончания аренды',
        'Status': 'Статус заявки',
        'Cost': 'Стоимость заявки',
        'CarId': 'Авто'
    },
    'clients': {
        'Name': 'Имя',
        'Surname': 'Фамилия',
        'Birthday': 'Дата рождения',
        'Phone': 'Телефон',
        'Email': 'Email',
        'CategoryVuID': 'Категории',
        'NumVU': 'Номер ВУ',
        'Password': 'Пароль'
    }
    }

def launch_client():
    choice_dict = {
        1: ['clients', 'registration', sign_up],
        2: ['clients', 'auth', sign_in],
        3: ['clients', 'get_client', get_client],
        4: ['clients', 'del_client', del_client],
        5: ['clients', 'edit_pass', edit_pass],
        6: ['clients', 'edit_client', edit_client],
        7: ['cars', 'get_cars', get_cars],
        8: ['cars', 'get_car', get_car],
        9: ['orders', 'add_order', add_order],
        10: ['orders', 'get_order', get_order],
        101: ['cars', 'edit_car', edit_car],
        100: ['clients', 'log_out', log_out],
    }
    try:
        client_socket.connect(('localhost', 9090))  # подключаемся к серверу
    except ConnectionRefusedError:
        print('Сервер не запущен')
        return False
    cprint('Клиент запущен!', 'yellow')
    client_data = {}  # словарь для отправки серверу

    while True:
        while True:
            if not ('token' in client_data):
                cprint('Выберите действие:', 'blue')
                print('Введите 1 чтобы зарегистрироваться:')
                print('Введите 2 чтобы авторизоваться:')
                print('Введите 0 чтобы завершить работу:')
            else:
                cprint('Выберите действие:', 'blue')
                print('Введите 3 чтобы посмотреть личную информацию')
                print('Введите 4 чтобы удалить ваш аккаунт')
                print('Введите 5 чтобы сменить пароль')
                print('Введите 6 чтобы изменить свои данные')
                print('Введите 7 чтобы посмотреть каталог')
                print('Введите 8 чтобы посмотреть авто')
                print('Введите 9 чтобы добавить заявку')
                print('Введите 10 чтобы посмотреть заявку')
                # print('Введите 9 чтобы изменить авто')
                print('Введите 100 чтобы выйти из аккаунта')
                print('Введите 0 чтобы завершить работу')
            try:
                choice = input()
                choice = int(choice)
            except ValueError:
                cprint('Ошибка! Введите цифру для выбора', 'red')
                break
            try:
                if choice == 0:
                    client_socket.close()
                    cprint('Заврешние работы...', 'blue')
                    return
                ch_dc = choice_dict.get(choice)
                client_data['endpoint'] = ch_dc[0]
                client_data['action'] = ch_dc[1]
                if (not 'token' in client_data and choice > 2):
                    cprint('Это действие доступно только для авторизованных пользователей!', 'red')
                    break
                elif ('token' in client_data and choice < 3):
                    cprint('Это действие недоступно!', 'red')
                    break
                client_data = ch_dc[2](client_data)
            except TypeError:
                cprint('Ошибка! Такого пункта нет!', 'red')
                break


def send_and_receive(client_data):
    send_data = json.dumps(client_data)
    client_socket.sendall(bytes(send_data, 'UTF-8'))  # отправка на сервер

    client_data = client_socket.recv(4096).decode()  # получение ответа от сервера
    client_data = json.loads(client_data)
    return client_data

def print_content(client_data):
    if 'Password' in client_data['content']:
        password = client_data['content']['Password']
        client_data['content']['Password'] = hashlib.sha256(password.encode()).hexdigest()

    client_data = send_and_receive(client_data)
    if client_data['status'] == '200':
        cprint(client_data['message'], 'green')
        print_client_data_fields(client_data)
    else:
        cprint(client_data['message'], 'red')
    return client_data


def input_client_data_fields(client_data):
    for field in fields_dict[client_data['endpoint']]:
        if field == 'Password':
            continue
        print('Введите ' + fields_dict[client_data['endpoint']][field])
        client_data['content'][field] = input()
    return client_data

def print_client_data_fields(client_data):
    for num in range(len(client_data['content'])):
        for field in fields_dict[client_data['endpoint']]:
            if field == 'Password':
                continue
            a = client_data['content'][num][field]
            if field in car_values_list:
                print(fields_dict[client_data['endpoint']][field] + ': ' + car_values_list[field][a])
            else:
                print(fields_dict[client_data['endpoint']][field] + ': ' + str(a))
        cprint("=" * 35, 'green')

###########CAR###############################################
def add_car(client_data):
    client_data['content'] = {}
    input_client_data_fields(client_data)
    client_data = print_content(client_data)
    return client_data

def delete_car():
    print('Введите id авто для удаления')
    choice_del = input()
    choice_del = int(choice_del)
    content = {'Id': choice_del}

    return content

def get_cars(client_data):
    print('Введите ' + fields_dict[client_data['endpoint']]['CategoryID'])
    choice_car = int(input())
    client_data['content'] = {}
    client_data['content']['CategoryID'] = choice_car
    client_data = print_content(client_data)

    return client_data

def get_car(client_data):
    print('Введите id авто')
    choice_car = int(input())
    client_data['content'] = {}
    client_data['content']['Id'] = choice_car
    client_data = print_content(client_data)

    return client_data

def edit_car(client_data):
    #  Поля отмеченные * - не обязательные или имеют значение по умолчанию
    #  Проблема с пустыми полями
    print('Введите Id ТС')
    client_data['content'] = {}
    client_data['content']['Id'] = int(input())
    input_client_data_fields(client_data)
    client_data = print_content(client_data)
    return client_data

###########CAR###############################################
###########Person###############################################

def sign_up(client_data):
    client_data['content'] = {}
    input_client_data_fields(client_data)
    client_data = print_content(client_data)
    return client_data

def sign_in(client_data):
    client_data['content'] = {}
    print('Введите ' + fields_dict[client_data['endpoint']]['Phone'])
    client_data['content']['Phone'] = input()
    print('Введите ' + fields_dict[client_data['endpoint']]['Password'])
    client_data['content']['Password'] = input()
    client_data = print_content(client_data)

    return client_data

def get_client(client_data):
    new_client_data = print_content(client_data)
    return new_client_data

def del_client(client_data):
    try:
        print('Вы уверены что хотите удалить аккаунт?' + '\n' + '0 - да 1 - нет')
        delete = input()
        if delete == '0':
            print_content(client_data)
            client_data = {}
    except ValueError:
        cprint('Ошибка! Введите цифру для выбора', 'red')

    return client_data

def log_out(client_data):
    client_data = {}
    cprint('Вы вышли из аккаунта!', 'blue')
    return client_data

def edit_pass(client_data):
    print('Введите новый пароль')
    new_password1 = str(input())
    print('Повторите пароль')
    new_password2 = str(input())
    if new_password1 == new_password2:
        client_data['content'] = {}
        client_data['content']['Password'] = new_password2
        client_data = print_content(client_data)
    else:
        cprint('Пароли не совпадают, попробуйте снова!', 'red')
    return client_data

def edit_client(client_data):
    client_data['content'] = {}
    input_client_data_fields(client_data)
    client_data = print_content(client_data)
    return client_data
###########Person###############################################
###########Order###############################################
def add_order(client_data):
    client_data['content'] = {}

    print('Введите Id авто')
    client_data['content']['CarId'] = input()
    print('Введите дату начала аренды в формате дд-мм-гггг')
    client_data['content']['DateStartContract'] = input()
    print('Введите дату конца аренды в формате дд-мм-гггг')
    client_data['content']['DateEndContract'] = input()
    client_data = print_content(client_data)
    return client_data

def get_order(client_data):
    print('Введите id заявки')
    choice_order = int(input())
    client_data['content'] = {}
    client_data['content']['Id'] = choice_order
    client_data = print_content(client_data)

    return client_data
launch_client()
