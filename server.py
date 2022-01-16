from decimal import Decimal

from sqlalchemy import create_engine, Integer, String, Column, Date, ForeignKey, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
import socket
import json
from sqlalchemy.orm import Session

db_engine = create_engine("postgresql+psycopg2://root:pass@localhost/postgres")

Base = declarative_base()

session = Session(bind=db_engine)


class Car(Base):
    __tablename__ = 'Cars'
    transmission_list = [
        (0, 'Механическая'),
        (1, 'Автоматическая')
    ]
    engine_list = [
        (0, 'Бензиновый'),
        (1, 'Дизельный')
    ]
    car_type_list = [
        (0, 'Седан'),
        (1, 'Кроссовер'),
        (2, 'Универсал'),
        (3, 'Хэтчбек'),
        (4, 'Купе'),
        (5, 'Микро')
    ]
    drive_list = [
        (0, 'Полный'),
        (1, 'Задний'),
        (2, 'Передний')
    ]
    wheel_drive_list = [
        (0, 'Правый'),
        (1, 'Левый')
    ]

    Id = Column(Integer, primary_key=True)  # pk
    CompanyID = Column(Integer, nullable=True)  # fk
    Location = Column(String(250), nullable=False)
    Photos = Column(String, default='')
    RentCondition = Column(String, default='Описание условий аренды')
    Header = Column(String, nullable=False)
    Driver = Column(Boolean, nullable=False)
    Status = Column(Boolean, nullable=True)
    CategoryID = Column(Integer, nullable=True)  # fk
    CategoryVU = Column(String, nullable=False)
    DateDel = Column(Date, nullable=True)
    FixedRate = Column(Numeric, nullable=True)
    Percent = Column(Numeric, nullable=True)

    Brand_and_name = Column(String, nullable=False)
    Transmission = Column(Integer, nullable=True, default=0)
    Engine = Column(Integer, nullable=True, default=0)
    Car_type = Column(Integer, nullable=True, default=0)
    Drive = Column(Integer, nullable=True, default=0)
    Wheel_drive = Column(Integer, nullable=True, default=0)
    Year = Column(Integer, nullable=False)
    Power = Column(Integer, nullable=False)
    Price = Column(Integer, nullable=False)

    def add_car(data):
        car = Car()
        # car.Photos = data['content']['Photos']
        car.Header = data['content']['Header']
        # car.CategoryID = data['content']['Photos']
        # car.CompanyID = request.POST.get('CompanyID')
        car.Brand_and_name = data['content']['Brand_and_name']
        car.Car_type = data['content']['Car_type']
        car.Engine = data['content']['Engine']
        car.Transmission = data['content']['Transmission']
        car.Drive = data['content']['Drive']
        car.Wheel_drive = data['content']['Wheel_drive']
        car.Year = data['content']['Year']
        car.Driver = data['content']['Driver']
        car.Status = data['content']['Status']
        car.Power = data['content']['Power']
        car.CategoryVU = data['content']['CategoryVU']
        car.Price = data['content']['Price']
        car.FixedRate = data['content']['FixedRate']
        car.Percent = data['content']['Percent']
        car.Location = data['content']['Location']
        car.RentCondition = data['content']['RentCondition']

        session.add(car)
        session.commit()
        data['content']['Id'] = car.Id
        data['Status'] = '200'
        return data

    def delete_car(data):
        car = session.query(Car).get(data['content']['Id'])
        if car is None:
            data['Status'] = '404'
        else:
            car.DateDel = date.today()
            session.commit()
            data['content']['Brand_and_name'] = car.Brand_and_name
            data['Status'] = '200'
        return data

    def get_car(data):
        car = session.query(Car).get(data['content']['Id'])
        if car is None:
            data['Status'] = '404'
        else:
            data['content']['CompanyID'] = car.CompanyID
            data['content']['Location'] = car.Location
            data['content']['Photos'] = car.Photos
            data['content']['RentCondition'] = car.RentCondition
            data['content']['Header'] = car.Header
            data['content']['Driver'] = car.Driver
            data['content']['CategoryID'] = car.CategoryID
            data['content']['CategoryVU'] = car.CategoryVU
            data['content']['FixedRate'] = car.FixedRate
            data['content']['Percent'] = car.Percent

            data['content']['Brand_and_name'] = car.Brand_and_name
            data['content']['Transmission'] = car.Transmission
            data['content']['Engine'] = car.Engine
            data['content']['Car_type'] = car.Car_type
            data['content']['Drive'] = car.Drive
            data['content']['Wheel_drive'] = car.Wheel_drive
            data['content']['Year'] = car.Year
            data['content']['Power'] = car.Power
            data['content']['Price'] = car.Price

            data['Status'] = '200'
        return data

    def get_cars(data):
        cars = session.query(Car).filter(Car.CategoryID == int(data['content']['CategoryID'])).all()
        new_cars = []  # [{} {} {}]
        if cars is None:
            data['Status'] = '404'
        else:
            for car in cars:
                dict = {}
                dict['Id'] = car.Id
                dict['CategoryID'] = car.CategoryID
                dict['CompanyID'] = car.CompanyID
                dict['Location'] = car.Location
                dict['Photos'] = car.Photos
                dict['RentCondition'] = car.RentCondition
                dict['Header'] = car.Header
                dict['Driver'] = car.Driver
                dict['CategoryID'] = car.CategoryID
                dict['CategoryVU'] = car.CategoryVU
                dict['FixedRate'] = car.FixedRate
                dict['Percent'] = car.Percent

                dict['Brand_and_name'] = car.Brand_and_name
                dict['Transmission'] = car.Transmission
                dict['Engine'] = car.Engine
                dict['Car_type'] = car.Car_type
                dict['Drive'] = car.Drive
                dict['Wheel_drive'] = car.Wheel_drive
                dict['Year'] = car.Year
                dict['Power'] = car.Power
                dict['Price'] = car.Price
                new_cars.append(dict)
            data['content'] = new_cars
            data['Status'] = '200'
        return data

    # def update_car(car, request, pk):
    #     car = Car.objects.get(id=pk)
    #     car.Header = request.POST.get('Header')
    #     car.CategoryID_id = request.POST.get('CategoryID')
    #     car.CompanyID_id = request.POST.get('CompanyID')
    #     car.Brand_and_name = request.POST.get('Brand_and_name')
    #     car.Car_type = request.POST.get('Car_type')
    #     car.Engine = request.POST.get('Engine')
    #     car.Transmission = request.POST.get('Transmission')
    #     car.Drive = request.POST.get('Drive')
    #     car.Wheel_drive = request.POST.get('Wheel_drive')
    #     car.Year = request.POST.get('Year')
    #     car.Driver = request.POST.get('Driver')
    #     car.Power = request.POST.get('Power')
    #     car.CategoryVUID = request.POST.get('CategoryVUID')
    #     car.Price = request.POST.get('Price')
    #     car.FixedRate = request.POST.get('FixedRate')
    #     car.Percent = request.POST.get('Percent')
    #     car.Location = request.POST.get('Location')
    #     car.RentCondition = request.POST.get('RentCondition')
    #     car.save()
    #     return car
    #
    #
    #
    # def hidden_car(pk):
    #     car = Car.objects.get(id=pk)
    #     car.Status = 1
    #     car.save()
    #     return car
    #
    # def visible_car(pk):
    #     car = Car.objects.get(id=pk)
    #     car.Status = 0
    #     car.save()
    #     return car


###########################################################################################################
# Base.metadata.create_all(db_engine)
def launch_server():
    ADDRESS = 'localhost'
    PORT = 9090

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
    server_socket.bind((ADDRESS, PORT))  # определяем адрес и порт
    server_socket.listen(1)  # прослушиваем порт от одного клиента
    print('Сервер запущен по адресу:', ADDRESS, PORT)
    ###########################################################################################################
    while True:
        connection, address = server_socket.accept()
        print('Клиент с адресом', address, ' подключен')
        while True:
            client_data = connection.recv(1024)  # client_data = {endpoint:cars, action:add, content:{fields....}}
            client_data = json.loads(client_data.decode())
            print(client_data)
            new_client_dict = client_data
            if client_data['endpoint'] == 'cars':
                if client_data['action'] == 'add':
                    new_client_dict = Car.add_car(new_client_dict)
                    print('Добавление авто', new_client_dict['Status'])
                if client_data['action'] == 'delete':
                    new_client_dict = Car.delete_car(new_client_dict)
                    print('Удаление авто', new_client_dict['Status'])
                if client_data['action'] == 'get':
                    new_client_dict = Car.get_car(new_client_dict)
                    print('Просмотр данных авто', new_client_dict['Status'])
                if client_data['action'] == 'get_cars':
                    new_client_dict = Car.get_cars(new_client_dict)
                    print('Просмотр всех авто', new_client_dict['Status'])

            connection.sendall(bytes(json.dumps(new_client_dict, ensure_ascii=False, default=str), 'UTF-8'))


launch_server()
