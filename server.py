from sqlalchemy import create_engine, Integer, String, Column, Date, ForeignKey, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date
import socket
import json
from sqlalchemy.orm import Session
import logging

# db_engine = create_engine("postgresql+psycopg2://root:pass@localhost/postgres")
db_engine = create_engine("sqlite:///database.db")
Base = declarative_base()
session = Session(bind=db_engine)
#########################################################################################
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] - %(levelname)s - %(name)s - %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
    filename="server_logger.log")
logger = logging.getLogger('server')
#########################################################################################

def object_to_dict(obj):  # преобразоваение объекта в словарь
    return {x.name: getattr(obj, x.name)
            for x in obj.__table__.columns}
#########################################################################################

class Car(Base):
    __tablename__ = 'Cars'

    Id = Column(Integer, primary_key=True)  # pk
    CompanyID = Column(Integer, nullable=True)  # fk
    Location = Column(String(250), nullable=False)
    Photos = Column(String, default='')
    RentCondition = Column(String, default='Описание условий аренды')
    Header = Column(String, nullable=False)
    Driver = Column(Boolean, nullable=False)
    status = Column(Boolean, nullable=True)
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
        try:
            car = Car(**data['content'])
            car.DateDel = None
            session.add(car)
            session.commit()
            data['status'] = '200'
            data['message'] = 'ТС с id ' + str(car.Id) + ' добавлено'
            logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'При добавлении клиента произошла ошибка'
            logger.info(data['message'] + ' ' + data['status'])

        return data

    def delete_car(data):
        try:
            car = session.query(Car).get(data['content']['Id'])
            car.DateDel = date.today()
            session.commit()
            data['status'] = '200'
            data['message'] = 'ТС с id ' + str(data['content']['Id']) + ' удалено'
            logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '404'
            data['message'] = 'ТС с id ' + str(data['content']['Id']) + ' не найдено'
            logger.info(str(data['message']) + ' ' + data['status'] )
        return data

    def get_car(data):
        try:
            car = session.query(Car).filter(Car.Id == int(data['content']['Id']), Car.DateDel == None).first()
            data['content'] = object_to_dict(car)
            data['status'] = '200'
            data['message'] = 'Просмотр ТС c id ' + str(data['content']['Id']) + ' ' + data['content']['Brand_and_name']
            logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '404'
            data['message'] = 'ТС с id ' + str(data['content']['Id']) + ' не найдено'
            logger.info(str(data['message']) + ' ' + data['status'])
        return data

    def get_cars(data):
        try:
            cars = session.query(Car).filter(Car.CategoryID == int(data['content']['CategoryID']), Car.DateDel == None).all()
            new_cars = []  # [{} {} {}]
            for car in cars:
                dict = object_to_dict(car)
                new_cars.append(dict)
            if new_cars:
                data['status'] = '200'
                data['message'] = 'Просмотр списка ТС с категорией ' + str(data['content']['CategoryID'])
                logger.info(data['message'] + ' ' + data['status'])
                data['content'] = new_cars
            else:
                data['status'] = '404'
                data['message'] = 'ТС с категорией ' + str(data['content']['CategoryID']) + ' нет'
                logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'При просмотре списка авто произошла ошибка'
            logger.error(data['message'] + ' ' + data['status'])

        return data

    def edit_car(data):
        try:
            car = session.query(Car).get(data['content']['Id'])
            if car is None:
                data['status'] = '404'
                data['message'] = 'ТС с id ' + str(data['content']['Id'] + ' не найдено!')
                logger.info(data['message'] + ' ' + data['status'])
            else:
                data['content']['DateDel'] = None
                # new_car = car.__dict__.update(data['content'])

                car.Photos = data['content']['Photos']
                car.Header = data['content']['Header']
                car.CategoryID = data['content']['CategoryID']
                car.CompanyID = data['content']['CompanyID']
                car.Brand_and_name = data['content']['Brand_and_name']
                car.Car_type = data['content']['Car_type']
                car.Engine = data['content']['Engine']
                car.Transmission = data['content']['Transmission']
                car.Drive = data['content']['Drive']
                car.Wheel_drive = data['content']['Wheel_drive']
                car.Year = data['content']['Year']
                car.Driver = data['content']['Driver']
                car.status = data['content']['status']
                car.Power = data['content']['Power']
                car.CategoryVU = data['content']['CategoryVU']
                car.Price = data['content']['Price']
                car.FixedRate = data['content']['FixedRate']
                car.Percent = data['content']['Percent']
                car.Location = data['content']['Location']
                car.RentCondition = data['content']['RentCondition']

                session.add(car)
                session.commit()
                data['status'] = '200'
                data['message'] = 'Редактирование ТС с id  ' + str(data['content']['Id'])
                logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Произошла ошибка редактирования ТС с id ' + str(data['content']['Id'])
            logger.info(data['message'] + ' ' + data['status'])
        return data

    # def hidden_car(pk):
    #     car = Car.objects.get(id=pk)
    #     car.status = 1
    #     car.save()
    #     return car
    #
    # def visible_car(pk):
    #     car = Car.objects.get(id=pk)
    #     car.status = 0
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
    logger.info('Сервер запущен по адресу: ' + ADDRESS + ':' + str(PORT))
###########################################################################################################
    cars_dict = {
        'add': Car.add_car,
        'delete': Car.delete_car,
        'get': Car.get_car,
        'get_cars': Car.get_cars,
        'edit_car': Car.edit_car
    }
    while True:
        connection, address = server_socket.accept()
        print('Клиент с адресом', address, ' подключен')
        logger.info('Клиент с адресом' + str(address) + ' подключен')
        while True:
            try:
                client_data = connection.recv(4096)
            except ConnectionResetError:
                print('Клиент с адресом', address, ' отключился')
                logger.info('Клиент с адресом' + str(address) + ' отключился')
                break
            if not client_data:
                print('Клиент с адресом', address, ' отключился')
                logger.info('Клиент с адресом' + str(address) + ' отключился')
                break
            client_data = json.loads(client_data.decode())
            print(client_data)
            new_client_dict = client_data
            if client_data['endpoint'] == 'cars':
                q = client_data['action']
                new_client_dict = cars_dict.get(q)(client_data)

            connection.sendall(bytes(json.dumps(new_client_dict, ensure_ascii=False, default=str), 'UTF-8'))


# Base.metadata.create_all(db_engine)
launch_server()
