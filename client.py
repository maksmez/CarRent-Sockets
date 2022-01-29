import json
import socket
from termcolor import colored, cprint

client_socket = socket.socket()  # создаем сокет

transmission_list = {
    0: 'Механическая',
    1: 'Автоматическая'
}
engine_list = {
    0: 'Бензиновый',
    1: 'Дизельный'
}
car_type_list = {
    0: 'Седан',
    1: 'Кроссовер',
    2: 'Универсал',
    3: 'Хэтчбек',
    4: 'Купе',
    5: 'Микро'
}
drive_list = {
    0: 'Полный',
    1: 'Задний',
    2: 'Передний'
}
wheel_drive_list = {
    0: 'Правый',
    1: 'Левый'
}


def launch_client():
    try:
        client_socket.connect(('localhost', 9090))  # подключаемся к серверу
    except ConnectionRefusedError:
        print('Сервер не запущен')
        return False
    print('Клиент запущен!')

    while True:
        print('Выберите действие:')
        print('Введите 1 чтобы добавить ТС')
        print('Введите 2 чтобы удалить ТС')
        print('Введите 3 чтобы посмотреть данные ТС')
        print('Введите 4 чтобы посмотреть все ТС')
        print('Введите 5 чтобы изменить ТС')

        print('Введите 0 чтобы отключиться')

        choice = input()
        choice = int(choice)

        client_data = {}  # словарь для отправки серверу
        if choice == 0:
            print('Завершение работы....')
            client_socket.close()
            break

        if choice < 6:
            client_data['endpoint'] = 'cars'
            if choice == 1:
                client_data['action'] = 'add'
                client_data['content'] = add_car()
                client_data = send_and_receive(client_data)
                cprint(client_data['message'], 'green')

            if choice == 2:
                client_data['action'] = 'delete'
                client_data['content'] = delete_car()
                client_data = send_and_receive(client_data)
                cprint(client_data['message'], 'green')

            if choice == 3:
                client_data['action'] = 'get'
                client_data['content'] = get_car()
                client_data = send_and_receive(client_data)
                if client_data['status'] == '200':
                    print("=" * 35)
                    cprint(client_data['message'], 'green')
                    print("="*35)
                    print('Id компании: ', client_data['content']['CompanyID'])
                    print('Адрес компании: ', client_data['content']['Location'])
                    print('Фотографии: ', client_data['content']['Photos'])
                    print('Условия аренды: ', client_data['content']['RentCondition'])
                    print('Заголовок: ', client_data['content']['Header'])
                    if client_data['content']['Driver'] == 'true':
                        print('Водитель: есть')
                    else:
                        print('Водитель: нет')
                    print('Id категории: ', client_data['content']['CategoryID'])
                    print('Категория ВУ: ', client_data['content']['CategoryVU'])
                    print('Фиксированная комиссия: ', client_data['content']['FixedRate'])
                    print('Процент комисии: ', client_data['content']['Percent'])
                    print('Марка и модель: ', client_data['content']['Brand_and_name'])
                    print('Трансмиссия: ', transmission_list[client_data['content']['Transmission']])
                    print('Двигатель: ', engine_list[client_data['content']['Engine']])
                    print('Кузов: ', car_type_list[client_data['content']['Car_type']])
                    print('Привод: ', drive_list[client_data['content']['Drive']])
                    print('Положения руля: ', wheel_drive_list[client_data['content']['Wheel_drive']])
                    print('Год выпуска: ', client_data['content']['Year'])
                    print('Мощность: ', client_data['content']['Power'])
                    print('Стоимость: ', client_data['content']['Price'])
                    print("=" * 35)
                else:
                    cprint(client_data['message'] + ' Код ответа: ' + client_data['status'], 'green')

            if choice == 4:
                client_data['action'] = 'get_cars'
                client_data['content'] = get_cars()
                client_data = send_and_receive(client_data)
                if client_data['status'] == '200':
                    print("=" * 35)
                    cprint(client_data['message'], 'green')
                    for car in client_data['content']:
                        print("=" * 35)
                        print('Данные авто c Id:', car['Id'])
                        print('Id компании: ', car['CompanyID'])
                        print('Адрес компании: ', car['Location'])
                        print('Фотографии: ', car['Photos'])
                        print('Условия аренды: ', car['RentCondition'])
                        print('Заголовок: ', car['Header'])
                        if car['Driver'] == 'true':
                            print('Водитель: есть')
                        else:
                            print('Водитель: нет')
                        print('Id категории: ', car['CategoryID'])
                        print('Категория ВУ: ', car['CategoryVU'])
                        print('Фиксированная комиссия: ', car['FixedRate'])
                        print('Процент комисии: ', car['Percent'])
                        print('Марка и модель: ', car['Brand_and_name'])
                        print('Трансмиссия: ', transmission_list[car['Transmission']])
                        print('Двигатель: ', engine_list[car['Engine']])
                        print('Кузов: ', car_type_list[car['Car_type']])
                        print('Привод: ',drive_list[car['Drive']])
                        print('Положения руля: ', wheel_drive_list[car['Wheel_drive']])
                        print('Год выпуска: ', car['Year'])
                        print('Мощность: ', car['Power'])
                        print('Стоимость: ', car['Price'])
                        print("=" * 35)
                else:
                    cprint(client_data['message'] + ' Код ответа: ' + client_data['status'], 'green')

            if choice == 5:
                client_data['action'] = 'edit_car'
                client_data['content'] = edit_car()
                client_data = send_and_receive(client_data)
                if client_data['status'] == '200':
                    cprint(client_data['message'], 'green')
                else:
                    cprint(client_data['message'] + ' Код ответа: ' + client_data['status'], 'green')


def send_and_receive(client_data):
    send_data = json.dumps(client_data)
    client_socket.sendall(bytes(send_data, 'UTF-8'))  # отправка на сервер

    client_data = client_socket.recv(4096).decode()  # получение ответа от сервера
    client_data = json.loads(client_data)
    return client_data

def add_car():
    #  Поля отмеченные * - не обязательные или имеют значение по умолчанию
    #  Проблема с пустыми полями
    content = {}

    print('Введите Id компании*')
    content['CompanyID'] = input()
    print('Введите адрес компании')
    content['Location'] = input()
    print('Введите пути к фотографиям*')
    content['Photos'] = input()
    print('Введите условия аренды*')
    content['RentCondition'] = input()
    print('Введите заголовок')
    content['Header'] = input()
    print('Есть ли водитель? 1 - да, 0 - нет')
    content['Driver'] = bool(input())
    content['status'] = True
    print('Введите ID категории*')
    content['CategoryID'] = input()
    print('Введите название категории ВУ')
    content['CategoryVU'] = input()
    content['DateDel'] = ''
    print('Введите фиксированную комиссию')
    content['FixedRate'] = input()
    print('Введите процент комиссии')
    content['Percent'] = input()

    print('Введите марку и название')
    content['Brand_and_name'] = input()
    print('Введите трансмиссию', '\n', '0 - механическая', '\n', '1 - автоматическая')
    content['Transmission'] = input()
    print('Введите двигатель*', '\n', '0 - бензиновый', '\n', '1 - дизельный')
    content['Engine'] = input()
    print('Введите типа кузова*' , '\n', '0 - Седан', '\n', '1 - Кроссовер', '\n', '2 - Универсал', '\n', '3 - Хэтчбек', '\n', '4 - Купе', '\n' , '5 - Микро')
    content['Car_type'] = input()
    print('Введите Привода*', '\n', '0 - Полный', '\n', '1 - Задний', '\n', '3 - Передний')
    content['Drive'] = input()
    print('Введите Положения руля*', '\n', '0 - Правый', '\n', '1 - Левый')
    content['Wheel_drive'] = input()
    print('Введите год выпуска')
    content['Year'] = input()
    print('Введите мощность')
    content['Power'] = input()
    print('Введите стоимость')
    content['Price'] = input()

    return content

def delete_car():
    print('Введите id авто для удаления')
    choice_del = input()
    choice_del = int(choice_del)
    content = {'Id': choice_del}

    return content

def get_cars():
    print('Введите id категории')
    choice_car = input()
    choice_car = int(choice_car)
    content = {'CategoryID': choice_car}

    return content

def get_car():
    print('Введите id авто')
    choice_car = input()
    choice_car = int(choice_car)
    content = {'Id': choice_car}

    return content

def edit_car():
    #  Поля отмеченные * - не обязательные или имеют значение по умолчанию
    #  Проблема с пустыми полями
    content = {}
    print('Введите Id ТС')
    content['Id'] = input()
    print('Введите Id компании*')
    content['CompanyID'] = input()
    print('Введите адрес компании')
    content['Location'] = input()
    print('Введите пути к фотографиям*')
    content['Photos'] = input()
    print('Введите условия аренды*')
    content['RentCondition'] = input()
    print('Введите заголовок')
    content['Header'] = input()
    print('Есть ли водитель? 1- да, 0 - нет')
    content['Driver'] = bool(input())
    content['status'] = True
    print('Введите ID категории*')
    content['CategoryID'] = input()
    print('Введите название категории ВУ')
    content['CategoryVU'] = input()
    content['DateDel'] = ''
    print('Введите фиксированную комиссию')
    content['FixedRate'] = input()
    print('Введите процент комиссии')
    content['Percent'] = input()

    print('Введите марку и название')
    content['Brand_and_name'] = input()
    print('Введите трансмиссию', '\n', '0 - механическая', '\n', '1 - автоматическая')
    content['Transmission'] = input()
    print('Введите двигатель*', '\n', '0 - бензиновый', '\n', '1 - дизельный')
    content['Engine'] = input()
    print('Введите типа кузова*' , '\n', '0 - Седан', '\n', '1 - Кроссовер', '\n', '2 - Универсал', '\n', '3 - Хэтчбек', '\n', '4 - Купе', '\n' , '5 - Микро')
    content['Car_type'] = input()
    print('Введите Привода*', '\n', '0 - Полный', '\n', '1 - Задний', '\n', '3 - Передний')
    content['Drive'] = input()
    print('Введите Положения руля*', '\n', '0 - Правый', '\n', '1 - Левый')
    content['Wheel_drive'] = input()
    print('Введите год выпуска')
    content['Year'] = input()
    print('Введите мощность')
    content['Power'] = input()
    print('Введите стоимость')
    content['Price'] = input()

    return content

launch_client()
