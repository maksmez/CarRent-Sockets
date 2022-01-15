import json
import socket

def launch_client():

    client_socket = socket.socket()  # создаем сокет
    client_socket.connect(('localhost', 9090))  # подключаемся к хосту

    while True:
        print('Введите 1 чтобы добавить ТС')
        choice = input()
        choice = int(choice)

        client_data = {}  # словарь для отправки серверу

        if choice == 1:
            client_data['endpoint'] = 'cars'
            client_data['action'] = 'add'
            client_data['content'] = add_car()



        send_data = json.dumps(client_data)
        client_socket.sendall(bytes(send_data, 'UTF-8'))

        client_data = client_socket.recv(1024).decode()
        client_data = json.loads(client_data)
        if  client_data['Status'] == '200':
            print('Авто ', client_data['content']['Brand_and_name'],  'добавлено!', client_data['Status'])
        else:
            print('При добавлении произошла ошибка! ', 'Ответ ', client_data['Status'])


def add_car():
    #  Поля отмеченные * - не обязательные или имеют значение по умолчанию
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
    content['Driver'] = input()
    content['Status'] = True
    print('Введите ID категории*')
    content['CategoryID'] = input()
    print('Введите название категории ВУ')
    content['CategoryVU'] = input()
    content['DateDel'] = None
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


launch_client()
