#  Перед запуском тестов в файле server.py нужно закомментировать строку accept_incoming_connections()!
import unittest
from time import sleep
from unittest.mock import patch
from decimal import Decimal
from server import *

class Test_1Person(unittest.TestCase):
    # проверяется клиент с id 13
    @patch('uuid.uuid4', return_value=uuid.UUID('06335e84-2872-4914-8c5d-3ed07d2a2f17'))
    def test_1_sign_in(self, mock_token):
        client_200_data = {'endpoint': 'clients', 'action': 'sign_in', 'content': {'Phone': '123456789', 'Password': '385cfdbc00ec32031699460779c15099b2bba3cad0e440fffb08e10df0acb9e1'}}
        expected_200_result = {'endpoint': 'clients', 'action': 'sign_in', 'content': [], 'status': '200', 'token': '06335e84287249148c5d3ed07d2a2f17', 'message': 'Вы авторизовались. Ваш id: 13'}
        result_200 = Person.sign_in(client_200_data)
        self.assertEqual(result_200, expected_200_result)


        client_404_data = {'endpoint': 'clients', 'action': 'sign_in', 'content': {'Phone': '111', 'Password': '385cfdbc00ec32031699460779c15099b2bba3cad0e440fffb08e10df0acb9e1'}}
        expected_404_result = {'endpoint': 'clients', 'action': 'sign_in', 'content': {'Phone': '111', 'Password': '385cfdbc00ec32031699460779c15099b2bba3cad0e440fffb08e10df0acb9e1'}, 'status': '404', 'message': 'Неверный телефон или пароль. Попробуйте снова. '}
        result_404 = Person.sign_in(client_404_data)
        self.assertEqual(result_404, expected_404_result)

    def test_2_log_out(self):
        client_200_data = {'endpoint': 'clients', 'action': 'log_out', 'content': [], 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_200_result = {'content': [], 'status': '200', 'message': 'Вы вышли из аккаунта!'}
        result_200 = Person.log_out(client_200_data)
        self.assertEqual(result_200, expected_200_result)

    # проверяется клиент с id 14
    @patch('uuid.uuid4', return_value=uuid.UUID('06335e84-2872-4914-8c5d-3ed07d2a2f18'))
    def test_3_sign_up(self, mock_token):
        client_200_data = {'endpoint': 'clients', 'action': 'sign_up', 'content': {'Id': 888, 'Name': 'test2', 'Surname': 'unit', 'Birthday': '01-01-2000', 'Phone': '987654321', 'Email': 'unit@mail.ru', 'CategoryVuID': 'a', 'NumVU': '11 aa', 'Password': '385cfdbc00ec32031699460779c15099b2bba3cad0e440fffb08e10df0acb9e1'}}
        expected_200_result = {'token': '06335e84287249148c5d3ed07d2a2f18', 'status': '200', 'content': [], 'message': 'Вы успешно зарегистрировались! Ваш Id: 888'}
        result_200 = Person.sign_up(client_200_data)
        self.assertEqual(result_200, expected_200_result)

        client_500_data = {'endpoint': 'clients', 'action': 'sign_up', 'content': {'Name': 'test2', 'Surname': 'unit', 'Birthday': '01-01-2000', 'Phone': '987654321', 'Email': 'unit@mail.ru', 'CategoryVuID': 'a','NumVU': '11 aa','Password': '385cfdbc00ec32031699460779c15099b2bba3cad0e440fffb08e10df0acb9e1'}}
        expected_500_result = {'action': 'sign_up', 'content': {'Birthday': '01-01-2000','CategoryVuID': 'a','Email': 'unit@mail.ru','Name': 'test2','NumVU': '11 aa','Password': '385cfdbc00ec32031699460779c15099b2bba3cad0e440fffb08e10df0acb9e1','Phone': '987654321','Surname': 'unit'},'endpoint': 'clients', 'message': 'Пользователь с таким телефоном уже зарегистрирован!', 'status': '500'}
        result_500 = Person.sign_up(client_500_data)
        self.assertEqual(result_500, expected_500_result)



    def test_4_get_client(self):
        client_200_data = {'endpoint': 'clients', 'action': 'get_client', 'content': [],'token': '06335e84287249148c5d3ed07d2a2f18'}
        expected_200_result = {'endpoint': 'clients', 'action': 'get_client', 'content': [{'Id': 888, 'CompanyID': 0, 'Name': 'test2', 'Surname': 'unit', 'Birthday': datetime.date(2000, 1, 1), 'Phone': '987654321', 'Email': 'unit@mail.ru', 'Position': 0, 'Comment': 'Я клиент', 'CategoryVuID': 'a', 'NumVU': '11 aa', 'DateDel': None}], 'status': '200', 'token': '06335e84287249148c5d3ed07d2a2f18', 'message': 'Данные клиента с id 888'}
        result_200 = Person.get_client(client_200_data)
        self.assertEqual(result_200, expected_200_result)

    def test_5_edit_client(self):
        client_200_data = {'endpoint': 'clients', 'action': 'edit_client', 'content': {'Name': 'unit2', 'Surname': 'test2', 'Birthday': '02-02-2000', 'Email': 'unit2@mail.ru', 'CategoryVuID': 'b', 'NumVU': '22 bb'}, 'token': '06335e84287249148c5d3ed07d2a2f18'}
        expected_200_result = {'endpoint': 'clients', 'action': 'edit_client', 'content': [], 'status': '200', 'message': 'Данные вашего аккаунта измнены! Ваш Id: 888', 'token': '06335e84287249148c5d3ed07d2a2f18'}
        result_200 = Person.edit_client(client_200_data)
        self.assertEqual(result_200, expected_200_result)

    def test_6_edit_pass(self):
        client_200_data = {'endpoint': 'clients', 'action': 'edit_pass', 'content': {'Password': '0efab319cc113a698ba482dd00dab8c25ee5537c2f974dc8cdc1c2fffdad46c7'}, 'token': '06335e84287249148c5d3ed07d2a2f18'}
        expected_200_result = {'endpoint': 'clients', 'action': 'edit_pass', 'content': [], 'status': '200', 'message': 'Пароль изменен! Ваш Id: 888', 'token': '06335e84287249148c5d3ed07d2a2f18'}
        result_200 = Person.edit_pass(client_200_data)
        self.assertEqual(result_200, expected_200_result)

        client_403_data = {'endpoint': 'clients', 'action': 'edit_pass', 'content': {'Password': '0efab319cc113a698ba482dd00dab8c25ee5537c2f974dc8cdc1c2fffdad46c7'}, 'token': '33'}
        expected_403_result = {'action': 'edit_pass','content': [],'endpoint': 'clients','message': 'Вы не авторизованы, действие запрещено','status': '403','token': '33'}
        result_403 = Person.edit_pass(client_403_data)
        self.assertEqual(result_403, expected_403_result)

    def test_7_del_client(self):
        client_200_data = {'endpoint': 'clients', 'action': 'del_client', 'content': [], 'token': '06335e84287249148c5d3ed07d2a2f18'}
        expected_200_result = {'endpoint': 'clients', 'action': 'del_client', 'content': [], 'status': '200', 'message': 'Аккаунт с id 888 удален', 'token': '06335e84287249148c5d3ed07d2a2f18'}
        result_200 = Person.del_client(client_200_data)
        self.assertEqual(result_200, expected_200_result)

        client_403_old_token_data = {'endpoint': 'clients', 'action': 'get_client', 'content': [], 'token': '06335e84287249148c5d3ed07d2a2f18'}
        expected_403_old_token_result = {'action': 'get_client', 'content': [], 'endpoint': 'clients', 'message': 'Время вашего сеанса истекло!\nАвторизируйтесь снова!', 'status': '403'}
        sleep(65)
        result_403_old_token_result = Person.get_client(client_403_old_token_data)
        self.assertEqual(result_403_old_token_result, expected_403_old_token_result)

class Test_2Car(unittest.TestCase):

    @patch('uuid.uuid4', return_value=uuid.UUID('06335e84-2872-4914-8c5d-3ed07d2a2f17'))
    def setUp(self, mock_token):
        client_data = {'endpoint': 'clients', 'action': 'sign_in', 'content': {'Phone': '123456789', 'Password': '385cfdbc00ec32031699460779c15099b2bba3cad0e440fffb08e10df0acb9e1'}}
        result = Person.sign_in(client_data) ##каждый раз заходит в эту функцию, а она отвечает за логинку при которой каждый раз добавляется токен по ид 13 и изз-за этого тарантул ругается

    def test_8_get_car(self):
        client_200_data = {'endpoint': 'cars', 'action': 'get_car', 'content': {'Id': 1}, 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_200_result = {'endpoint': 'cars', 'action': 'get_car', 'content': [{'Id': 1, 'CompanyID': 1, 'Location': 'вфывыф', 'Photos': '-', 'RentCondition': '-', 'Header': '-', 'Driver': True, 'status': True, 'CategoryID': 1, 'CategoryVU': 'B', 'DateDel': None, 'FixedRate': Decimal('12.0000000000'), 'Percent': Decimal('2.0000000000'), 'Brand_and_name': 'Kia Rio', 'Transmission': 0, 'Engine': 0, 'Car_type': 0, 'Drive': 0, 'Wheel_drive': 0, 'Year': 2009, 'Power': 223, 'Price': 2300}], 'status': '200', 'token': '06335e84287249148c5d3ed07d2a2f17', 'message': 'Просмотр ТС c id 1'}
        result_200 = Car.get_car(client_200_data)
        self.assertEqual(result_200, expected_200_result)

        client_404_data = {'endpoint': 'cars', 'action': 'get_car', 'content': {'Id': 200000}, 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_404_result = {'action': 'get_car', 'content': {'Id': 200000}, 'endpoint': 'cars', 'message': 'ТС с id 200000 не найдено', 'status': '404','token': '06335e84287249148c5d3ed07d2a2f17'}
        result_404 = Car.get_car(client_404_data)
        self.assertEqual(result_404, expected_404_result)

    def test_9_get_cars(self):
        client_200_data = {'endpoint': 'cars', 'action': 'get_cars', 'content': {'CategoryID': 1}, 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_200_result = {'endpoint': 'cars', 'action': 'get_cars', 'content': [{'Id': 1, 'CompanyID': 1, 'Location': 'вфывыф', 'Photos': '-', 'RentCondition': '-', 'Header': '-', 'Driver': True, 'status': True, 'CategoryID': 1, 'CategoryVU': 'B', 'DateDel': None, 'FixedRate': Decimal('12.0000000000'), 'Percent': Decimal('2.0000000000'), 'Brand_and_name': 'Kia Rio', 'Transmission': 0, 'Engine': 0, 'Car_type': 0, 'Drive': 0, 'Wheel_drive': 0, 'Year': 2009, 'Power': 223, 'Price': 2300}], 'status': '200', 'token': '06335e84287249148c5d3ed07d2a2f17', 'message': 'Просмотр списка ТС с категорией 1'}
        result_200 = Car.get_cars(client_200_data)
        self.assertEqual(result_200, expected_200_result)

        client_404_no_category_data = {'endpoint': 'cars', 'action': 'get_cars', 'content': {'CategoryID': 1000}, 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_404_no_category_result = {'action': 'get_cars', 'content': {'CategoryID': 1000}, 'endpoint': 'cars', 'message': 'Категории с id 1000 нет', 'status': '404','token': '06335e84287249148c5d3ed07d2a2f17'}
        result_404_no_category = Car.get_cars(client_404_no_category_data)
        self.assertEqual(result_404_no_category, expected_404_no_category_result)

        client_404_no_cars_data = {'endpoint': 'cars', 'action': 'get_cars', 'content': {'CategoryID': 3}, 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_404_no_cars_result = {'action': 'get_cars', 'content': {'CategoryID': 3}, 'endpoint': 'cars', 'message': 'ТС с категорией 3 нет', 'status': '404', 'token': '06335e84287249148c5d3ed07d2a2f17'}
        result_404_no_cars = Car.get_cars(client_404_no_cars_data)
        self.assertEqual(result_404_no_cars, expected_404_no_cars_result)

class Test_3Contract(unittest.TestCase):
    @patch('uuid.uuid4', return_value=uuid.UUID('06335e84-2872-4914-8c5d-3ed07d2a2f17'))
    def setUp(self, mock_token):
        client_data = {'endpoint': 'clients', 'action': 'sign_in', 'content': {'Phone': '123456789', 'Password': '385cfdbc00ec32031699460779c15099b2bba3cad0e440fffb08e10df0acb9e1'}}
        result = Person.sign_in(client_data)

    def test_10_add_order(self):
        client_404_no_order_data = {'endpoint': 'orders', 'action': 'get_orders', 'content': [], 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_404_no_order_result = {'action': 'get_orders', 'content': [], 'endpoint': 'orders', 'message': 'Заявок у клиента с id 13 нет!', 'status': '404', 'token': '06335e84287249148c5d3ed07d2a2f17'}
        result_404_no_order = Contract.get_orders(client_404_no_order_data)
        self.assertEqual(result_404_no_order, expected_404_no_order_result)

        client_200_data = {'endpoint': 'orders', 'action': 'add_order', 'content': {'Id': '888', 'CarId': '1', 'DateStartContract': '20-01-2020', 'DateEndContract': '20-02-2020'} ,'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_200_result = {'endpoint': 'orders', 'action': 'add_order', 'content': [], 'status': '200', 'message': 'Заявка добавлена! Id заявки: 888', 'token': '06335e84287249148c5d3ed07d2a2f17'}
        result_200 = Contract.add_order(client_200_data)
        self.assertEqual(result_200, expected_200_result)

        client_404_data = {'endpoint': 'orders', 'action': 'add_order', 'content': {'Id': '888', 'CarId': '10000', 'DateStartContract': '20-01-2020', 'DateEndContract': '20-02-2020'} ,'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_404_result = {'action': 'add_order', 'content': {'CarId': '10000', 'DateEndContract': '20-02-2020', 'DateStartContract': '20-01-2020', 'Id': '888'}, 'endpoint': 'orders', 'message': 'Автомобиль не найден!', 'status': '500', 'token': '06335e84287249148c5d3ed07d2a2f17'}
        result_404 = Contract.add_order(client_404_data)
        self.assertEqual(result_404, expected_404_result)

    def test_11_get_order(self):
        client_200_data = {'endpoint': 'orders', 'action': 'get_order', 'content': {'Id': 888},'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_200_result = {'endpoint': 'orders', 'action': 'get_order', 'content': [{'Id': 888, 'ClientId': 13, 'CarId': 'Kia Rio: id 1', 'DateStartContract': datetime.date(2020, 1, 20), 'DateEndContract': datetime.date(2020, 2, 20), 'Driver': False, 'Note': None, 'Status': 0, 'Comission': Decimal('1438.0000000000'), 'Cost': 71300, 'DateDel': None}], 'status': '200', 'token': '06335e84287249148c5d3ed07d2a2f17', 'message': 'Просмотр заявки c id 888'}
        result_200 = Contract.get_order(client_200_data)
        self.assertEqual(result_200, expected_200_result)

        client_404_data = {'endpoint': 'orders', 'action': 'get_order', 'content': {'Id': 100000},'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_404_result = {'action': 'get_order', 'content': {'Id': 100000}, 'endpoint': 'orders', 'message': 'Заявка с id 100000 не найдена', 'status': '404', 'token': '06335e84287249148c5d3ed07d2a2f17'}
        result_404 = Contract.get_order(client_404_data)
        self.assertEqual(result_404, expected_404_result)

    def test_12_get_orders(self):
        client_200_data = {'endpoint': 'orders', 'action': 'get_orders', 'content': [], 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_200_result = {'action': 'get_orders', 'content': [{'CarId': 'Kia Rio: id 1', 'ClientId': 13, 'Comission': Decimal('1438.0000000000'), 'Cost': 71300, 'DateDel': None, 'DateEndContract': datetime.date(2020, 2, 20), 'DateStartContract': datetime.date(2020, 1, 20), 'Driver': False, 'Id': 888, 'Note': None, 'Status': 0}], 'endpoint': 'orders', 'message': 'Просмотр заявок клиента с id 13', 'status': '200', 'token': '06335e84287249148c5d3ed07d2a2f17'}
        result_200 = Contract.get_orders(client_200_data)
        self.assertEqual(result_200, expected_200_result)


class Test_4Favorite(unittest.TestCase):
    @patch('uuid.uuid4', return_value=uuid.UUID('06335e84-2872-4914-8c5d-3ed07d2a2f17'))
    def setUp(self, mock_token):
        client_data = {'endpoint': 'clients', 'action': 'sign_in', 'content': {'Phone': '123456789', 'Password': '385cfdbc00ec32031699460779c15099b2bba3cad0e440fffb08e10df0acb9e1'}}
        result = Person.sign_in(client_data)

    def test_13_add_favorite(self):
        client_404_no_cars_data = {'endpoint': 'clients', 'action': 'get_favorites', 'content': [], 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_404_no_cars_result = {'action': 'get_favorites', 'content': [], 'endpoint': 'clients', 'message': 'Список избранного у клиента с id 13 пуст!', 'status': '404', 'token': '06335e84287249148c5d3ed07d2a2f17'}
        result_404_no_cars = Favorite.get_favorites(client_404_no_cars_data)
        self.assertEqual(result_404_no_cars, expected_404_no_cars_result)

        client_200_data = {'endpoint': 'clients', 'action': 'add_favorite', 'content': {'Id': 888, 'CarId': 1}, 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_200_result = {'endpoint': 'clients', 'action': 'add_favorite', 'content': [], 'token': '06335e84287249148c5d3ed07d2a2f17', 'status': '200', 'message': 'Авто добавлено в избранное! Id авто: 1'}
        result_200 = Favorite.add_favorite(client_200_data)
        self.assertEqual(result_200, expected_200_result)

        client_500_data = {'endpoint': 'clients', 'action': 'add_favorite', 'content': {'Id': 888, 'CarId': 1}, 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_500_result = {'action': 'add_favorite', 'content': {'CarId': 1, 'Id': 888}, 'endpoint': 'clients', 'message': 'Авто с id 1 уже добавлено в избранное!', 'status': '500', 'token': '06335e84287249148c5d3ed07d2a2f17'}
        result_500 = Favorite.add_favorite(client_500_data)
        self.assertEqual(result_500, expected_500_result)

        client_404_data = {'endpoint': 'clients', 'action': 'add_favorite', 'content': {'Id': 888, 'CarId': 100000}, 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_404_result = {'action': 'add_favorite', 'content': {'CarId': 100000, 'Id': 888}, 'endpoint': 'clients', 'message': 'Автомобиль не найден!', 'status': '500', 'token': '06335e84287249148c5d3ed07d2a2f17'}
        result_404 = Favorite.add_favorite(client_404_data)
        self.assertEqual(result_404, expected_404_result)

    def test_14_get_favorites(self):
        client_200_data = {'endpoint': 'clients', 'action': 'get_favorites', 'content': [], 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_200_result = {'endpoint': 'clients', 'action': 'get_favorites', 'content': [{'CarId': 'Kia Rio: id 1'}], 'token': '06335e84287249148c5d3ed07d2a2f17', 'status': '200', 'message': 'Просмотр списка избранного клиента с id 13'}
        result_200 = Favorite.get_favorites(client_200_data)
        self.assertEqual(result_200, expected_200_result)


    def test_15_del_favorite(self):
        client_200_data = {'endpoint': 'clients', 'action': 'del_favorite', 'content': {'CarId': 1}, 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_200_result = {'endpoint': 'clients', 'action': 'del_favorite', 'content': [], 'token': '06335e84287249148c5d3ed07d2a2f17', 'status': '200', 'message': 'ТС с id 1 удалено из избранного'}
        result_200 = Favorite.del_favorite(client_200_data)
        self.assertEqual(result_200, expected_200_result)

        client_data = {'endpoint': 'clients', 'action': 'del_favorite', 'content': {'CarId': 10000}, 'token': '06335e84287249148c5d3ed07d2a2f17'}
        expected_result = {'action': 'del_favorite', 'content': {'CarId': 10000}, 'endpoint': 'clients', 'message': 'ТС с id 10000 не найдено в избранном', 'status': '404', 'token': '06335e84287249148c5d3ed07d2a2f17'}
        result = Favorite.del_favorite(client_data)
        self.assertEqual(result, expected_result)



# class MyTestCase(unittest.TestCase):
#     @unittest.skip("Запуск сервера")
#     def test_launch_server(self):
#         self.fail("Пропуск")

if __name__ == '__main__':
    unittest.main()


















