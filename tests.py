import pytest
from main import User
from main import Goods
from main import Purchase
from main import test_app, create_app, db
import jwt
import datetime


@pytest.fixture()
def createapp():
    app = create_app()
    app.app_context().push()


@pytest.fixture()
def login_the_user():
    app = create_app()
    app.app_context().push()
    app.testing = True
    client = app.test_client()
    global token
    user_id = User.query.filter_by(login=log).first().id
    token = jwt.encode({'id': user_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=25)},
                       app.config['SECRET_KEY'])
    yield client
    app.testing = False


class TestCreateUser:

    # miss the field - login
    def test1(self):
        data = {'password': '1111', 'name': 'naz123'}
        test1 = test_app.post('/UserCreate', json=data)
        assert test1.status_code == 200
        assert test1.get_json() == [{'message': 'Invalid input'}, 400]

    # miss the field - name
    def test2(self):
        data = {'login': 'Nazar', 'password': '1111'}
        test2 = test_app.post('/UserCreate', json=data)
        assert test2.status_code == 200
        assert test2.get_json() == [{'message': 'Invalid input'}, 400]

    # miss the field - password
    def test3(self):
        data = {'login': 'Nazar', 'name': 'naz123'}
        test3 = test_app.post('/UserCreate', json=data)
        assert test3.status_code == 200
        assert test3.get_json() == [{'message': 'Invalid input'}, 400]

    # check on exist user
    def test4(self):
        data = {'login': 'Nazar', 'password': '1111', 'name': 'naz123'}
        test4 = test_app.post('/UserCreate', json=data)
        assert test4.status_code == 200
        assert test4.get_json() == [{"message": "User exist with such login"}, 409]

    # try to create user
    def test5(self, createapp):
        data = {'login': 'Nazar', 'password': '1111', 'name': 'naz123'}
        global log
        log = data['login']
        test5 = test_app.post('/UserCreate', json=data)
        assert test5.status_code == 200
        assert User.query.filter_by(login=str(data['login'])).first() is not None


class TestLogin:

    # no input data
    def test1(self):
        test1 = test_app.get('/log_in', json=None)
        assert test1.status_code == 401

    # incorrect login
    def test2(self):
        data = {'login': 'Noname', 'password': '55555'}
        test2 = test_app.get('/log_in', json=data)
        assert test2.status_code == 401

    # incorrect password
    def test3(self):
        data = {'login': 'Nazar', 'password': '1234'}
        test3 = test_app.get('/log_in', json=data)
        assert test3.status_code == 401

    # incorrect login and password
    def test4(self):
        data = {'login': 'Nazarko', 'password': '12345'}
        test4 = test_app.get('/log_in', json=data)
        assert test4.status_code == 401

    # correct login and password
    def test5(self):
        data = {'login': 'Nazar', 'password': '1111'}
        test5 = test_app.get('/log_in', json=data)
        assert test5.status_code == 200


class TestEditUser:

    def test1(self, login_the_user):
        data = {"new_username": "new_naz123"}
        headers = {'x-access-token': token}
        test1 = test_app.put('/UserUpdate', json=data, headers=headers)
        assert test1.status_code == 200
        assert test1.get_json() == [{'message': 'User was updated'}, 200]

    def test2(self, login_the_user):
        data = {'new_password': "2222"}
        headers = {'x-access-token': token}
        test2 = test_app.put('/UserUpdate', json=data, headers=headers)
        assert test2.status_code == 200
        assert test2.get_json() == [{'message': 'User was updated'}, 200]


class TestDeleteUser:

    def test1(self, login_the_user):
        headers = {'x-access-token': token}
        test1 = test_app.delete('/UserDelete', headers=headers)
        assert test1.status_code == 200
        assert User.query.filter_by(login=log).first() is None


@pytest.fixture()
def login_the_user_1():
    app = create_app()
    app.app_context().push()
    app.testing = True
    client1 = app.test_client()
    global token
    user = User.query.filter_by(login='Tor').first()
    token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=25)},
                       app.config['SECRET_KEY'])
    yield client1
    app.testing = False


class TestCreateGoods:

    def test1(self, login_the_user_1):
        data = {'tag': "Mazda", 'description': "This is electric car", 'price': '43563262',
                'amount': '3', 'login': 'Tor'}
        headers = {'x-access-token': token}
        test1 = test_app.post('/GoodsCreate', json=data, headers=headers)

        global id_goods
        id_goods = Goods.query.filter_by(tag=data['tag']).first().id

        assert test1.status_code == 200
        assert test1.get_json() == [{"message": "Goods was created"}, 200]

    # miss the description
    def test2(self, login_the_user_1):
        data = {'tag': "Mazda", 'price': '43563262', 'amount': '3', 'login': 'Tor'}
        headers = {'x-access-token': token}
        test2 = test_app.post('/GoodsCreate', json=data, headers=headers)
        assert test2.status_code == 200
        assert test2.get_json() == [{"message": "Invalid input"}, 400]

    # miss the tag
    def test3(self, login_the_user_1):
        data = {'description': "This is electric car", 'price': '43563262', 'amount': '3', 'login': 'Tor'}
        headers = {'x-access-token': token}
        test3 = test_app.post('/GoodsCreate', json=data, headers=headers)
        assert test3.status_code == 200
        assert test3.get_json() == [{"message": "Invalid input"}, 400]

    # miss the price
    def test4(self, login_the_user_1):
        data = {'tag': "Mazda", 'description': "This is electric car", 'amount': '3', 'login': 'Tor'}
        headers = {'x-access-token': token}
        test4 = test_app.post('/GoodsCreate', json=data, headers=headers)
        assert test4.status_code == 200
        assert test4.get_json() == [{"message": "Invalid input"}, 400]

    # miss the price
    def test5(self, login_the_user_1):
        data = {'tag': "Mazda", 'description': "This is electric car", 'amount': '3', 'login': 'Tor'}
        headers = {'x-access-token': token}
        test5 = test_app.post('/GoodsCreate', json=data, headers=headers)
        assert test5.status_code == 200
        assert test5.get_json() == [{"message": "Invalid input"}, 400]

