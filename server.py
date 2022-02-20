import decimal
import hashlib
import uuid

import yaml
from sqlalchemy import create_engine, Integer, String, Column, Date, ForeignKey, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
import socket
import json
from sqlalchemy.orm import Session, relationship
import logging.config
import datetime
import tarantool
import threading

with open('config_server') as config_server:
    config = yaml.safe_load(config_server)

#########################################################################################
logging.config.dictConfig(config['logger_settings'])
logger = logging.getLogger('server')
#########################################################################################

# tarantool_space.insert((7,'7777a2sd7as2d7a7d7asd7adasdas'))  # вставка данных (id и token должны быть уникальными т.к индексы)
# tarantool_space.replace((5, '111112nhfhsfhsdfhsdhf'))  # изменение данных
# tarantool_space.delete((6))  # удаляет запись по id
# connection_tarantool.call('box.space.user_token:truncate', ())  # удаление всех записей
# print(tarantool_space.select())  # поиск записи по id, если (), то вывод всех


try:
    connection_tarantool = tarantool.connect(config['connection_string_tarantool_ip'],
                                             config['connection_string_tarantool_port'])
    tarantool_space = connection_tarantool.space('user_token')
    # db_engine = create_engine(config['connection_string'])
    db_engine = create_engine(config['connection_string'])
    db_engine.connect()
    Base = declarative_base()
    session = Session(bind=db_engine)
except tarantool.error.NetworkError:
    logger.error('Tarantool не подключен!!')
    exit()
except:
    logger.error('SQLite не подключен!!')
    exit()

salt = config['salt']


#########################################################################################
def object_to_dict(obj):  # преобразоваение объекта в словарь
    return {x.name: getattr(obj, x.name)
            for x in obj.__table__.columns}

#########################################################################################
def dict_to_object(obj, dict):
    for x in obj.__table__.columns:
        if x.name in dict:
            setattr(obj, x.name, dict[x.name])
    return obj
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
    # car_favorite = relationship("Favorite", back_populates="favorite_car")

    Brand_and_name = Column(String, nullable=False)
    Transmission = Column(Integer, nullable=True, default=0)
    Engine = Column(Integer, nullable=True, default=0)
    Car_type = Column(Integer, nullable=True, default=0)
    Drive = Column(Integer, nullable=True, default=0)
    Wheel_drive = Column(Integer, nullable=True, default=0)
    Year = Column(Integer, nullable=False)
    Power = Column(Integer, nullable=False)
    Price = Column(Integer, nullable=False)

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
                logger.error(str(data['message']) + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера'
            logger.error(str(data['message']) + ' ' + data['status'])
        return data

    def get_cars(data):
        try:
            category = session.query(Category).get(int(data['content']['CategoryID']))
            if category == None:
                data['status'] = '404'
                data['message'] = 'Категории с id ' + str(data['content']['CategoryID']) + ' нет'
                logger.error(data['message'] + ' ' + data['status'])
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
                    logger.error(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'При просмотре списка авто произошла ошибка'
            logger.error(data['message'] + ' ' + data['status'])

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
    favorites = relationship("Car", secondary="Favorites")

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
                tarantool_space.insert(
                    (person.Id, person.Token))  # вставка данных (id и token должны быть уникальными т.к индексы)
                new_data['token'] = person.Token
                new_data['status'] = '200'
                new_data['content'] = []
                new_data['message'] = 'Вы успешно зарегистрировались! Ваш Id: ' + str(person.Id)
                logger.info(new_data['message'] + ' ' + new_data['status'])
            else:
                new_data['status'] = '500'
                new_data['message'] = 'Пользователь с таким телефоном уже зарегистрирован!'
                logger.error(new_data['message'] + ' ' + new_data['status'])
        except:
            new_data['status'] = '500'
            new_data['message'] = 'При регистрации произошла ошибка'
            logger.error(new_data['message'] + ' ' + new_data['status'])
        return new_data

    def sign_in(data):
        try:
            salted = hashlib.sha256(data['content']['Password'].encode() + salt.encode()).hexdigest()
            man = session.query(Person).filter(Person.Phone == data['content']['Phone'], Person.Password == salted,
                                               Person.DateDel == None).first()
            if man is not None:
                data['content'] = []
                data['status'] = '200'
                data['token'] = man.Token
                data['message'] = 'Вы авторизовались. ' + 'Ваш id: ' + str(man.Id)
                logger.info(data['message'] + ' ' + data['status'])
            else:
                data['status'] = '404'
                data['message'] = 'Неверный телефон или пароль. Попробуйте снова. '
                logger.error(str(data['message']) + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера'
            logger.error(str(data['message']) + ' ' + data['status'])
        return data

    def get_client(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            data['content'] = [object_to_dict(man)]
            del (data['content'][0]['Password'])
            del (data['content'][0]['Token'])
            data['token'] = man.Token
            data['status'] = '200'
            data['message'] = 'Данные клиента с id ' + str(man.Id)
            logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'При просмотре информации произошла ошибка'
            logger.error(data['message'] + ' ' + data['status'])
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
            logger.error(str(data['message']) + ' ' + data['status'])

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
                logger.error(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'При смене пароля произошла ошибка'
            data['token'] = data['token']
            logger.error(data['message'] + ' ' + data['status'])
        return data

    def edit_client(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            if man is not None:
                man = dict_to_object(man, data['content'])
                man.Birthday = datetime.datetime.strptime(data['content']['Birthday'], "%d-%m-%Y")
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
                logger.error(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'При изменении произошла ошибка'
            logger.error(data['message'] + ' ' + data['status'])
        return data

    def log_out(data):
        try:
            # man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            # строка для удаления токена?????
            data = {}
            data['content'] = []
            data['status'] = '200'
            data['message'] = 'Вы вышли из аккаунта!'
            client_data = {}
            logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера!'
            logger.error(data['message'] + ' ' + data['status'])
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
                contract.DateStartContract = datetime.datetime.strptime(data['content']['DateStartContract'],
                                                                        "%d-%m-%Y")
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
                logger.error(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера'
            logger.error(data['message'] + ' ' + data['status'])
        return data

    def get_order(data):
        try:
            contract = session.query(Contract).filter(Contract.Id == int(data['content']['Id']),
                                                      Contract.DateDel == None).first()
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            l = list(filter(lambda x: x.Id == int(data['content']['Id']), man.client_contracts))
            contract = l[0] if l != [] else None
            if contract is not None:
                data['content'] = [object_to_dict(contract)]
                c = contract.contract_car.Id
                data['content'][0]['CarId'] = contract.contract_car.Brand_and_name + ': id ' + str(
                    contract.contract_car.Id)
                data['status'] = '200'
                data['message'] = 'Просмотр заявки c id ' + str(data['content'][0]['Id'])
                logger.info(data['message'] + ' ' + data['status'])
            else:
                data['status'] = '404'
                data['message'] = 'Заявка с id ' + str(data['content']['Id']) + ' не найдена'
                logger.error(str(data['message']) + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера'
            logger.error(str(data['message']) + ' ' + data['status'])
        return data

    def get_orders(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            list_contract = list(man.client_contracts)
            contracts = []
            for o in list_contract:
                object = object_to_dict(o)
                c = o.contract_car
                object['CarId'] = c.Brand_and_name + ': id ' + str(c.Id)
                contracts.append(object)
            if contracts:
                data['content'] = contracts
                data['status'] = '200'
                data['message'] = 'Просмотр заявок клиента с id ' + str(man.Id)
                logger.info(data['message'] + ' ' + data['status'])
            else:
                data['status'] = '404'
                data['message'] = 'Заявок у клиента с id ' + str(man.Id) + ' нет!'
                logger.error(str(data['message']) + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера'
            logger.error(str(data['message']) + ' ' + data['status'])
        return data


class Favorite(Base):
    __tablename__ = 'Favorites'
    Id = Column(Integer, primary_key=True)  # pk
    ClientId = Column(Integer, ForeignKey('Person.Id'), nullable=False)  # fk
    CarId = Column(Integer, ForeignKey('Cars.Id'), nullable=False)  # fk
    Date_add = Column(Date, nullable=True)
    DateDel = Column(Date, nullable=True)
    # favorite_client = relationship("Person", back_populates="client_favorite")
    # favorite_car = relationship("Car", back_populates="car_favorite")

    def add_favorite(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            car = session.query(Car).filter(Car.Id == data['content']['CarId'], Car.DateDel == None).first()
            # a = man.client_favorite
            if man is not None:
                if car not in man.favorites:
                    fav = Favorite()
                    fav.CarId = car.Id
                    fav.ClientId = man.Id
                    fav.Date_add = datetime.date.today()
                    session.add(fav)
                    session.commit()
                    data['content'] = []
                    data['status'] = '200'
                    data['message'] = 'Авто добавлено в избранное! Id авто: ' + str(car.Id)
                    logger.info(data['message'] + ' ' + data['status'])
                else:
                    data['status'] = '500'
                    data['message'] = 'Авто с id ' + str(car.Id) + ' уже добавлено в избранное!'
                    logger.error(data['message'] + ' ' + data['status'])
            else:
                data['status'] = '500'
                data['message'] = 'Пользователь не найден!'
                logger.error(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера'
            logger.error(data['message'] + ' ' + data['status'])
        return data

    def del_favorite(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            fav = session.query(Favorite).filter(Favorite.ClientId == man.Id,
                                                 Favorite.CarId == data['content']['CarId']).first()
            # fav.DateDel = datetime.date.today()
            session.delete(fav)
            session.commit()
            data['content'] = []
            data['status'] = '200'
            data['message'] = 'ТС с id ' + str(fav.CarId) + ' удалено из избранного'
            logger.info(data['message'] + ' ' + data['status'])
        except:
            data['status'] = '404'
            data['message'] = 'ТС с id ' + str(data['content']['CarId']) + ' не найдено в избранном'
            logger.error(str(data['message']) + ' ' + data['status'])
        return data

    def get_favorites(data):
        try:
            man = session.query(Person).filter(Person.Token == data['token'], Person.DateDel == None).first()
            list_favorites = list(man.favorites)
            favorites = []
            for o in list_favorites:
                object = {}
                object['CarId'] = o.Brand_and_name + ': id ' + str(o.Id)
                favorites.append(object)
            if favorites:
                data['content'] = favorites
                data['status'] = '200'
                data['message'] = 'Просмотр списка избранного клиента с id ' + str(man.Id)
                logger.info(data['message'] + ' ' + data['status'])
            else:
                data['status'] = '404'
                data['message'] = 'Список избранного у клиента с id ' + str(man.Id) + ' пуст!'
                logger.error(str(data['message']) + ' ' + data['status'])
        except:
            data['status'] = '500'
            data['message'] = 'Ошибка сервера'
            logger.error(str(data['message']) + ' ' + data['status'])
        return data


###########################################################################################################
client_count = threading.BoundedSemaphore(2)
client_data = {}


def launch_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # создаем сокет
    server_socket.bind((config['ADDRESS'], config['PORT']))  # определяем адрес и порт
    server_socket.listen()  # прослушиваем порт от одного клиента
    logger.info('Сервер запущен по адресу: ' + config['ADDRESS'] + ':' + str(config['PORT']))
    ###########################################################################################################
    cars_dict = {
        'get_cars': Car.get_cars,
        'get_car': Car.get_car
    }
    person_dict = {
        'sign_up': Person.sign_up,
        'sign_in': Person.sign_in,
        'get_client': Person.get_client,
        'del_client': Person.del_client,
        'edit_pass': Person.edit_pass,
        'edit_client': Person.edit_client,
        'log_out': Person.log_out,
        'add_favorite': Favorite.add_favorite,
        'del_favorite': Favorite.del_favorite,
        'get_favorites': Favorite.get_favorites
    }
    contract_dict = {
        'add_order': Contract.add_order,
        'get_order': Contract.get_order,
        'get_orders': Contract.get_orders,
    }

    while True:
        connection, address = server_socket.accept()
        client_count.acquire()
        print('Количество доступных подключений: ', client_count._value)
        logger.info('Клиент с адресом' + str(address) + ' подключен')
        while True:
            try:
                client_data = connection.recv(4096)
            except ConnectionResetError:
                logger.info('Клиент с адресом' + str(address) + ' отключился')
                client_count.release()
                print('Количество доступных подключений: ', client_count._value)
                break
            if not client_data:
                logger.info('Клиент с адресом' + str(address) + ' отключился')
                client_count.release()
                print('Количество доступных подключений: ', client_count._value)
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
            client_data = {}
            connection.sendall(bytes(json.dumps(new_client_dict, ensure_ascii=False, default=str), 'UTF-8'))


# Base.metadata.create_all(db_engine)
launch_server()
