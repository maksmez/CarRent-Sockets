import hashlib
import json
import socket
import struct

from termcolor import cprint

client_socket = socket.socket()  # создаем сокет

car_values_list = {
    'Transmission': ['Механическая', 'Автоматическая'],
    'Engine': ['Бензиновый', 'Дизельный'],
    'Car_type': ['Седан', 'Кроссовер', 'Универсал', 'Хэтчбек', 'Купе', 'Микро'],
    'Drive': ['Полный', 'Задний', 'Передний'],
    'Wheel_drive': ['Правый', 'Левый']
}
order_status_dict = {
    'Status': ['Активная','Завершена','Отменена']
}

fields_dict = {
    'cars': {
        'CompanyID': 'Id компании',
        'Location': 'Адрес компании',
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
        'Id': 'Id заявки',
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
    },
    'favorites': {
        'CarId': 'Авто'
    }
}


def launch_client():
    choice_dict = {
        1: ['clients', 'sign_up', sign_up, 'чтобы зарегистрироваться'],
        2: ['clients', 'sign_in', sign_in, 'чтобы авторизоваться'],
        3: ['clients', 'get_client', get_client, 'посмотреть личную информацию:'],
        4: ['clients', 'del_client', del_client, 'чтобы удалить ваш аккаунт'],
        5: ['clients', 'edit_pass', edit_pass, 'чтобы сменить пароль'],
        6: ['clients', 'edit_client', edit_client, 'чтобы изменить свои данные'],
        7: ['cars', 'get_cars', get_cars, 'чтобы посмотреть каталог'],
        8: ['cars', 'get_car', get_car, 'чтобы посмотреть авто'],
        9: ['orders', 'add_order', add_order, 'чтобы добавить заявку'],
        10: ['orders', 'get_order', get_order, 'чтобы посмотреть заявку'],
        11: ['orders', 'get_orders', get_orders, 'чтобы посмотреть заявки'],
        12: ['clients', 'add_favorite', add_favorite, 'чтобы добавить ТС в избранное'],
        13: ['clients', 'del_favorite', del_favorite, 'чтобы удалить ТС из избранного'],
        14: ['clients', 'get_favorites', get_favorites, 'чтобы просмотреть список избранного'],
        15: ['clients', 'log_out', log_out, 'чтобы выйти из аккаунта'],
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
            cprint('Выберите действие:', 'blue')
            if not ('token' in client_data):
                for i in range(1, 3):
                    print('Введите', i, choice_dict[i][3])
            else:
                for i in range(3, len(choice_dict) + 1):
                    print('Введите', i, choice_dict[i][3])
            try:
                cprint('Введите 0 - для завершения работы', 'red')
                choice = int(input())
            except ValueError:
                cprint('Ошибка! Введите цифру для выбора', 'red')
                break
            try:
                if choice == 0:
                    client_socket.close()
                    cprint('Завершение работы...', 'blue')
                    return
                ch_dc = choice_dict.get(choice)
                client_data['endpoint'] = ch_dc[0]
                client_data['action'] = ch_dc[1]
                if not 'token' in client_data and choice > 2:
                    cprint('Это действие доступно только для авторизованных пользователей!', 'red')
                    break
                elif 'token' in client_data and choice < 3:
                    cprint('Это действие недоступно!', 'red')
                    break
                client_data = ch_dc[2](client_data)
            except Exception as e:
                print(e)
            except TypeError:
                cprint('Ошибка! Такого пункта нет!', 'red')
                break
            except ValueError:
                cprint('Ошибка, проверьте введенные данные!', 'red')
                break

def recvall(sock, n):
    # Функция для получения n байт или возврата None если получен EOF
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def recv_msg(sock):
    # Получение длины сообщения и распаковка в integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Получение данных
    return recvall(sock, msglen).decode()

def send_and_receive(client_data):
    # send_data = json.dumps(client_data)
    # client_socket.sendall(bytes(send_data, 'UTF-8'))  # отправка на сервер
    send_data = json.dumps(client_data)
    send_data = bytes(send_data.encode())
    msg = struct.pack('>I', len(send_data)) + send_data
    client_socket.sendall(msg)

    client_data = recv_msg(client_socket)
    # client_data = client_socket.recv(4096).decode()  # получение ответа от сервера
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
    del(client_data['message'])
    del(client_data['status'])
    return client_data


def input_client_data_fields(client_data):
    for field in fields_dict[client_data['endpoint']]:
        if (field == 'Password' or field == 'Phone') and (client_data['action'] == 'edit_client'):
            continue
        print('Введите ' + fields_dict[client_data['endpoint']][field])
        client_data['content'][field] = input()
    return client_data


def print_client_data_fields(client_data):
    if client_data['content']:
        cprint("=" * 35, 'green')
        for num in range(len(client_data['content'])):
            if client_data['action'] == 'get_favorites':
                print(fields_dict['favorites']['CarId'] + ': ' + client_data['content'][num]['CarId'])
            else:
                for field in fields_dict[client_data['endpoint']]:
                    if field == 'Password':
                        continue
                    a = client_data['content'][num][field]
                    if field in car_values_list:
                        print(fields_dict[client_data['endpoint']][field] + ': ' + car_values_list[field][a])
                    else:
                        if field in order_status_dict:
                            print(fields_dict[client_data['endpoint']][field] + ': ' + order_status_dict[field][a])
                        else:
                            print(fields_dict[client_data['endpoint']][field] + ': ' + str(a))

            cprint("=" * 35, 'green')
    else:
        return

def check_id():
    choice = int(input())
    return choice
###########CAR###############################################
def get_cars(client_data):
    print('Введите ' + fields_dict[client_data['endpoint']]['CategoryID'])
    client_data['content'] = {}
    client_data['content']['CategoryID'] = check_id()
    client_data = print_content(client_data)
    return client_data


def get_car(client_data):
    print('Введите id авто')
    client_data['content'] = {}
    choice_car = check_id()
    client_data['content']['Id'] = choice_car
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
    client_data = print_content(client_data)
    return client_data


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
    client_data = print_content(client_data)
    client_data = {}
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
    choice_order = check_id()
    client_data['content'] = {}
    client_data['content']['Id'] = choice_order
    client_data = print_content(client_data)

    return client_data


def get_orders(client_data):
    client_data = print_content(client_data)
    return client_data
###########Order###############################################


###########Favorite###############################################
def add_favorite(client_data):
    print('Введите id ТС')
    choice_car = check_id()
    client_data['content'] = {}
    client_data['content']['CarId'] = choice_car
    client_data = print_content(client_data)
    return client_data


def del_favorite(client_data):
    print('Введите id ТС для удаления из избранного')
    choice_car = check_id()
    client_data['content'] = {}
    client_data['content']['CarId'] = choice_car
    client_data = print_content(client_data)
    return client_data


def get_favorites(client_data):
    client_data = print_content(client_data)
    return client_data
###########Favorite###############################################



launch_client()
