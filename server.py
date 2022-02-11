import decimal
import hashlib
import uuid
from uuid import uuid4

from sqlalchemy import create_engine, Integer, String, Column, Date, ForeignKey, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
import datetime
import socket
import json
from sqlalchemy.orm import Session, relationship
import logging
import configparser
import datetime

config = configparser.ConfigParser()  # создаём объект парсера
config.read("config.ini")

# db_engine = create_engine("postgresql+psycopg2://root:pass@localhost/postgres")
db_engine = create_engine("sqlite:///database.db")
Base = declarative_base()
session = Session(bind=db_engine)
salt = config['Salt']['salt']

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
    CompanyID = Column(Integer, ForeignKey('Company.Id'), nullable=False)  # fk
    Location = Column(String(250), nullable=False)
    Photos = Column(String, default='')
    RentCondition = Column(String, default='Описание условий аренды')
    Header = Column(String, nullable=False)
    Driver = Column(Boolean, nullable=False)
    status = Column(Boolean, nullable=True)
    CategoryID = Column(Integer, ForeignKey('Category.Id'), nullable=False)  # fk
    CategoryVU = Column(String, nullable=False)
    DateDel = Column(Date, nullable=True)
    FixedRate = Column(Numeric, nullable=True)
    Percent = Column(Numeric, nullable=True)
    car_company = relationship("Company", back_populates="company_cars")
    car_category = relationship("Category", back_populates="category_cars")
    car_contract = relationship("Contract", back_populates="contract_car")

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
            car.status = True
            if data['content']['Driver'] == '1':
                car.Driver = True
            else:
                car.Driver = False
            session.add(car)
            session.commit()
            data['status'] = '200'
            data['message'] = 'ТС с id ' + str(car.Id) + ' добавлено'
            logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'При добавлении ТС произошла ошибка'
            logger.info(data['message'] + ' ' + data['status'])

        return data

    def delete_car(data):
        try:
            car = session.query(Car).get(data['content']['Id'])
            car.DateDel = datetime.date.today()
            session.commit()
            data['status'] = '200'
            data['message'] = 'ТС с id ' + str(data['content']['Id']) + ' удалено'
            logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '404'
            data['message'] = 'ТС с id ' + str(data['content']['Id']) + ' не найдено'
            logger.info(str(data['message']) + ' ' + data['status'])
        return data

    def get_car(data):
        try:
            car = session.query(Car).filter(Car.Id == int(data['content']['Id']), Car.DateDel == None).first()
            if car is not None:
                data['content'] = [object_to_dict(car)]
                data['status'] = '200'
                data['message'] = 'Просмотр ТС c id ' + str(data['content'][0]['Id'])
                logger.info(data['message'] + ' ' + data['status'])
            else:
                data['status'] = '404'
                data['message'] = 'ТС с id ' + str(data['content']['Id']) + ' не найдено'
                logger.info(str(data['message']) + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера'
            logger.info(str(data['message']) + ' ' + data['status'])
        return data

    def get_cars(data):
        try:
            category = session.query(Category).get(int(data['content']['CategoryID']))
            if category == None:
                data['status'] = '404'
                data['message'] = 'Категории с id ' + str(data['content']['CategoryID']) + ' нет'
                logger.info(data['message'] + ' ' + data['status'])
            else:
                cars = category.category_cars
                new_cars = []  # [{} {} {}]
                for car in cars:
                    if car.DateDel == None:
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
                if data['content']['Driver'] == '1':
                    car.Driver = True
                else:
                    car.Driver = False
                # car.status = data['content']['status']
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


class Person(Base):
    __tablename__ = 'Person'
    Id = Column(Integer, primary_key=True)  # pk
    CompanyID = Column(Integer, nullable=True, default=0)  # fk
    Name = Column(String, nullable=False)
    Surname = Column(String, nullable=False)
    Birthday = Column(Date, nullable=True)
    Phone = Column(String, nullable=False)
    Password = Column(String, nullable=False)
    Token = Column(String, nullable=False)
    Email = Column(String, nullable=True)
    Position = Column(Integer, nullable=True)
    Comment = Column(String, nullable=True)
    CategoryVuID = Column(String, nullable=False)
    NumVU = Column(String, nullable=False)
    DateDel = Column(Date, nullable=True)
    client_contracts = relationship("Contract", back_populates="contract_client")
    def sign_up(data):
        try:
            new_data = data
            man = session.query(Person).filter(Person.Phone == data['content']['Phone'], Person.DateDel == None).first()
            if man is None:
                salted = hashlib.sha256(data['content']['Password'].encode() + salt.encode()).hexdigest()
                data['content']['Password'] = salted
                person = Person(**data['content'])
                person.Birthday = datetime.datetime.strptime(data['content']['Birthday'], "%d-%m-%Y")
                person.DateDel = None
                person.CompanyID = None
                person.Position = 0
                person.Comment = 'Я клиент'
                person.Token = uuid.uuid4().hex
                session.add(person)
                session.commit()
                new_data['token'] = person.Token
                new_data['status'] = '200'
                new_data['content'] = []
                new_data['message'] = 'Вы успешно зарегистрировались! Ваш Id: ' + str(person.Id)
                logger.info(new_data['message'] + ' ' + new_data['status'])
            else:
                new_data['status'] = '500'
                new_data['message'] = 'Пользователь с таким телефоном уже зарегистрирован!'
                logger.info(new_data['message'] + ' ' + new_data['status'])
        except:
            new_data['status'] = '500'
            new_data['message'] = 'При регистрации произошла ошибка'
            logger.info(new_data['message'] + ' ' + new_data['status'])
        return new_data

    def sign_in(data):
        try:
            salted = hashlib.sha256(data['content']['Password'].encode() + salt.encode()).hexdigest()
            man = session.query(Person).filter(Person.Phone == data['content']['Phone'], Person.Password == salted, Person.DateDel == None).first()
            if man is not None:
                data['content'] = []
                data['status'] = '200'
                data['token'] = man.Token
                data['message'] = 'Вы авторизовались. ' + 'Ваш id: ' + str(man.Id)
                logger.info(data['message'] + ' ' + data['status'])
            else:
                data['status'] = '404'
                data['message'] = 'Неверный телефон или пароль. Попробуйте снова. '
                logger.info(str(data['message']) + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера'
            logger.info(str(data['message']) + ' ' + data['status'])
        return data

    def get_client(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            data['content'] = [object_to_dict(man)]
            del(data['content'][0]['Password'])
            del(data['content'][0]['Token'])
            data['token'] = man.Token
            data['status'] = '200'
            data['message'] = 'Данные клиента с id ' + str(man.Id)
            logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'При просмотре информации произошла ошибка'
            logger.info(data['message'] + ' ' + data['status'])
        return data

    def del_client(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            man.DateDel = datetime.date.today()
            session.add(man)
            session.commit()
            data['content'] = []
            data['status'] = '200'
            data['message'] = 'Аккаунт с id ' + str(man.Id) + ' удален'
            logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка на сервере'
            logger.info(str(data['message']) + ' ' + data['status'])

        return data

    def edit_pass(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            if man is not None:
                salted = hashlib.sha256(data['content']['Password'].encode() + salt.encode()).hexdigest()
                man.Password = salted
                session.add(man)
                session.commit()
                data['content'] = []
                data['status'] = '200'
                data['token'] = man.Token
                data['message'] = 'Пароль изменен! Ваш Id: ' + str(man.Id)
                logger.info(data['message'] + ' ' + data['status'])
            else:
                data['status'] = '500'
                data['message'] = 'Пользователь с таким телефоном не найден!'
                logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'При смене пароля произошла ошибка'
            data['token'] = data['token']
            logger.info(data['message'] + ' ' + data['status'])
        return data

    def edit_client(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            if man is not None:
                man.Name = data['content']['Name']
                man.Surname = data['content']['Surname']
                man.Birthday = datetime.datetime.strptime(data['content']['Birthday'], "%d-%m-%Y")
                man.Email = data['content']['Email']
                man.CategoryVuID = data['content']['CategoryVuID']
                man.NumVU = data['content']['NumVU']
                session.add(man)
                session.commit()
                data['content'] = []
                data['token'] = man.Token
                data['status'] = '200'
                data['message'] = 'Данные вашего аккаунта измнены! Ваш Id: ' + str(man.Id)
                logger.info(data['message'] + ' ' + data['status'])
            else:
                data['status'] = '404'
                data['message'] = 'Пользователь не найден!'
                logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'При изменении произошла ошибка'
            logger.info(data['message'] + ' ' + data['status'])
        return data


class Company(Base):
    __tablename__ = 'Company'
    Id = Column(Integer, primary_key=True)  # pk
    Name = Column(String, nullable=False)
    Phone = Column(String, nullable=False)
    Email = Column(String, nullable=True)
    Note = Column(String, nullable=True)
    DateDel = Column(Date, nullable=True)
    FIOContact = Column(String, nullable=False)
    ContactPhone = Column(String, nullable=False)
    ContactEmail = Column(String, nullable=True)
    company_cars = relationship("Car", back_populates="car_company")


class Category(Base):
    __tablename__ = 'Category'
    Id = Column(Integer, primary_key=True)  # pk
    NameCat = Column(String, nullable=False)
    Icon = Column(String, nullable=True)
    DateDel = Column(Date, nullable=True)
    category_cars = relationship("Car", back_populates="car_category")


class Contract(Base):
    __tablename__ = 'Contract'
    Id = Column(Integer, primary_key=True)  # pk
    ClientId = Column(Integer, ForeignKey('Person.Id'), nullable=False)  # fk
    CarId = Column(Integer, ForeignKey('Cars.Id'), nullable=False)  # fk
    DateStartContract = Column(Date, nullable=False)
    DateEndContract = Column(Date, nullable=False)
    Driver = Column(Boolean, nullable=False)
    Note = Column(String, nullable=True)
    Status = Column(Integer, nullable=False)
    Comission = Column(Numeric, nullable=False)
    Cost = Column(Integer, nullable=False)
    DateDel = Column(Date, nullable=True)
    contract_client = relationship("Person", back_populates="client_contracts")
    contract_car = relationship("Car", back_populates="car_contract")

    def add_order(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            car = session.query(Car).filter(Car.Id == data['content']['CarId'], Car.DateDel == None).first()
            if man is not None:
                start = datetime.datetime.strptime(data['content']['DateStartContract'], "%d-%m-%Y")
                end = datetime.datetime.strptime(data['content']['DateEndContract'], "%d-%m-%Y")
                if end == start:
                    rez = 1
                else:
                    rez = (end - start).days
                cost = rez * car.Price
                car_per = car.Percent
                car_fix = car.FixedRate
                per1 = car_per * decimal.Decimal(0.01)
                per2 = round((per1 * decimal.Decimal(cost)) + car_fix, 2)

                contract = Contract(**data['content'])
                contract.DateStartContract = datetime.datetime.strptime(data['content']['DateStartContract'], "%d-%m-%Y")
                contract.DateEndContract = datetime.datetime.strptime(data['content']['DateEndContract'], "%d-%m-%Y")
                contract.ClientId = man.Id
                contract.CarId = car.Id
                contract.Cost = cost
                contract.Comission = per2
                contract.Driver = False
                contract.Status = 0
                session.add(contract)
                session.commit()
                data['content'] = []
                data['status'] = '200'
                data['message'] = 'Заявка добавлена! Id заявки: ' + str(contract.Id)
                logger.info(data['message'] + ' ' + data['status'])
            else:
                data['status'] = '500'
                data['message'] = 'Пользователь не найден!'
                logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера'
            logger.info(data['message'] + ' ' + data['status'])
        return data

    def get_order(data):
        # try:
        contract = session.query(Contract).filter(Contract.Id == int(data['content']['Id']), Contract.DateDel == None).first()
        man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
        l = list(filter(lambda x: x.Id == int(data['content']['Id']), man.client_contracts))
        contract = l[0] if l != [] else None
        if contract is not None:
            data['content'] = [object_to_dict(contract)]
            c = contract.contract_car.Id
            data['content'][0]['CarId'] = contract.contract_car.Brand_and_name + ': id ' + str(contract.contract_car.Id)
            data['status'] = '200'
            data['message'] = 'Просмотр заявки c id ' + str(data['content'][0]['Id'])
            logger.info(data['message'] + ' ' + data['status'])
        else:
            data['status'] = '404'
            data['message'] = 'Заявка с id ' + str(data['content']['Id']) + ' не найдена'
            logger.info(str(data['message']) + ' ' + data['status'])
        # except:
        #     data['status'] = '500'
        #     data['message'] = 'Ошибка сервера'
        #     logger.info(str(data['message']) + ' ' + data['status'])
        return data
###########################################################################################################
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
        'edit_car': Car.edit_car,
        'add_car': Car.add_car,
        'get_car': Car.get_car
    }
    person_dict = {
        'registration': Person.sign_up,
        'auth': Person.sign_in,
        'get_client': Person.get_client,
        'del_client': Person.del_client,
        'edit_pass': Person.edit_pass,
        'edit_client': Person.edit_client
    }

    contract_dict = {
        'add_order': Contract.add_order,
        'get_order': Contract.get_order,
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
            if client_data['endpoint'] == 'clients':
                q = client_data['action']
                new_client_dict = person_dict.get(q)(client_data)
            if client_data['endpoint'] == 'orders':
                q = client_data['action']
                new_client_dict = contract_dict.get(q)(client_data)
            connection.sendall(bytes(json.dumps(new_client_dict, ensure_ascii=False, default=str), 'UTF-8'))


# Base.metadata.create_all(db_engine)
launch_server()
