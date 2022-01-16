import json
import socket


def launch_client():
    try:
        client_socket = socket.socket()  # создаем сокет
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

        print('Введите 0 чтобы отключиться')

        choice = input()
        choice = int(choice)

        client_data = {}  # словарь для отправки серверу

        if choice == 1:
            client_data['endpoint'] = 'cars'
            client_data['action'] = 'add'
            client_data['content'] = add_car()

        if choice == 2:
            client_data['endpoint'] = 'cars'
            client_data['action'] = 'delete'
            client_data['content'] = delete_car()

        if choice == 3:
            client_data['endpoint'] = 'cars'
            client_data['action'] = 'get'
            client_data['content'] = get_car()

        if choice == 4:
            client_data['endpoint'] = 'cars'
            client_data['action'] = 'get_cars'
            client_data['content'] = get_cars()

        if choice == 0:
            print('Завершение работы....')
            client_socket.close()
            break

        send_data = json.dumps(client_data)
        client_socket.sendall(bytes(send_data, 'UTF-8'))  # отправка на сервер

        client_data = client_socket.recv(1024).decode()  # получение ответа от сервера
        client_data = json.loads(client_data)

        if choice == 1:
            if client_data['Status'] == '200':
                print('Авто ', client_data['content']['Brand_and_name'], 'добавлено!', client_data['Status'])
            else:
                print('При добавлении произошла ошибка! ', 'Ответ ', client_data['Status'])

        if choice == 2:
            if client_data['Status'] == '200':
                print('Авто ', client_data['content']['Brand_and_name'], 'удалено!', client_data['Status'])
            else:
                print('При удалении произошла ошибка! ', 'Ответ ', client_data['Status'])

        if choice == 3:
            if client_data['Status'] == '200':
                print('Данные авто:')
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
                print('Id трансмиссии: ', client_data['content']['Transmission'])
                print('Id двигателя: ', client_data['content']['Engine'])
                print('Id кузова: ', client_data['content']['Car_type'])
                print('Id привода: ', client_data['content']['Drive'])
                print('Id положения руля: ', client_data['content']['Wheel_drive'])
                print('Год выпуска: ', client_data['content']['Year'])
                print('Мощность: ', client_data['content']['Power'])
                print('Стоимость: ', client_data['content']['Price'])
            else:
                print('При получении информации произошла ошибка! ', 'Ответ ', client_data['Status'])

        if choice == 4:
            if client_data['Status'] == '200':
                print('Список авто')
                for car in client_data['content']:
                    print('                     Данные авто c Id:', car['Id'])
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
                    print('Id трансмиссии: ', car['Transmission'])
                    print('Id двигателя: ', car['Engine'])
                    print('Id кузова: ', car['Car_type'])
                    print('Id привода: ', car['Drive'])
                    print('Id положения руля: ', car['Wheel_drive'])
                    print('Год выпуска: ', car['Year'])
                    print('Мощность: ', car['Power'])
                    print('Стоимость: ', car['Price'])
            else:
                print('При получении информации произошла ошибка! ', 'Ответ ', client_data['Status'])

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
    print('Есть ли водитель? True or False')
    content['Driver'] = bool(input())
    content['Status'] = True
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
    print('Введите Id трансмиссии*')
    content['Transmission'] = input()
    print('Введите Id двигателя*')
    content['Engine'] = input()
    print('Введите Id типа кузова*')
    content['Car_type'] = input()
    print('Введите Id привода*')
    content['Drive'] = input()
    print('Введите Id положения руля*')
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
    content = {}
    content['Id'] = choice_del

    return content

def get_cars():
    print('Введите id категории')
    choice_car = input()
    choice_car = int(choice_car)
    content = {}
    content['CategoryID'] = choice_car

    return content

def get_car():
    print('Введите id авто')
    choice_car = input()
    choice_car = int(choice_car)
    content = {}
    content['Id'] = choice_car

    return content


launch_client()
