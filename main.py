from flask import Flask, render_template, request, jsonify, make_response
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate, MigrateCommand
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
import jwt

# instantiate the app
app = Flask(__name__)
# app config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'Just a key'

# instantiate db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# instantiate manage
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# instantiate ma
ma = Marshmallow(app)


# User Scheme
class UserScheme(ma.Schema):
    class Meta:
        fields = ('id', 'login', 'password', 'username')


# instantiate User Scheme
user_scheme = UserScheme()
users_scheme = UserScheme(many=True)


# Purchase Model
class Purchase(db.Model):
    __tablename__ = "purchase"

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'))
    customer = db.relationship('User', backref='owner')
    goods_create = db.relationship('Goods', backref='goods')
    text = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, customer=None, goods_create=None, text=None):
        self.customer = customer
        self.goods_create = goods_create
        self.text = text


# User Model
class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer(), primary_key=True)
    login = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(40), unique=True, nullable=False)
    username = db.Column(db.String(40), unique=True, nullable=False)

    def __init__(self, login=None, password=None, username=None):
        self.login = login
        self.password = password
        self.username = username

    def update_info(self, idi=None, login=None, password=None, username=None):
        # get user from db by his `id`
        if idi:
            # get user from db by his `id`
            update_user = User.query.filter_by(id=idi).first()
            update_user.login = login
            update_user.password = generate_password_hash(password)
            update_user.username = username
            db.session.commit()
            return jsonify({"message": "User was updated"}, 200)
        else:
            return jsonify({"message": "Invalid input"}, 404)

    def read_from_db(self, idi=None):
        # get user from db by his `id`
        if idi:
            read_user = User.query.filter_by(id=idi).first()
            return user_scheme.jsonify(read_user)
        else:
            return jsonify({"message": "Invalid id"}, 404)

    def delete_from_db(self, id_of_d=None):
        # delete user from db by his `id`
        if id_of_d:
            delete_user = User.query.get(id_of_d)
            db.session.delete(delete_user)
            db.session.commit()
            return jsonify({"message": "User was deleted"}, 200)
        else:
            return jsonify({"message": "User wont deleted"}, 404)


# Goods Model
class Goods(db.Model):
    __tablename__ = "goods"

    id = db.Column(db.Integer(), primary_key=True)
    tag = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    amount = db.Column(db.Integer(), nullable=False)

    # every goods has its customer
    customer_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    # one-to-many (one user - many goods)
    users = db.relationship('User', backref='customer')

    def __init__(self, tag=None, description=None, price=None, amount=None, users=None):
        self.tag = tag
        self.description = description
        self.price = price
        self.amount = amount
        self.users = users

    def read_by_tag(self, tag=None):
        if tag:
            goods = Goods.query.filter_by(tag=tag).all()
            for item in goods:
                print("Name of goods:", item.tag)
                print("Description of goods:", item.description)
                print("The price of goods:", item.price)
                print("The amount of goods:", item.amount)
                print("The customer id =", item.customer_id)
                print()
            return jsonify({"message": "Goods with this tag: "}, 200)
        else:
            return jsonify({"message": "Error"}, 404)

    def read_by_user_id(self, user=None):
        if user:
            userid = Goods.query.filter_by(customer_id=user).all()
            for item in userid:
                print("Name of goods:", item.tag)
                print("Description of goods:", item.description)
                print("The price of goods:", item.price)
                print("The amount of goods:", item.amount)
                print("The customer id =", item.customer_id)
                print()
            return jsonify({"message": "Goods by user_id: "}, 200)
        else:
            return jsonify({"message": "Error"}, 404)

    def goods_update(self, goods_data=None):
        if goods_data:
            user_id = goods_data.get('user_id')
            goods_id = goods_data.get('goods_id')
            read_user = User.query.filter_by(id=user_id).first()
            read_goods = Goods.query.filter_by(id=goods_id).first()
            goods_customer = read_goods.customer_id
            info_by_goods_id = Purchase.query.filter_by(goods_id=goods_id).all()

            # check if user id has access
            if goods_customer != user_id and user_id not in info_by_goods_id:
                if len(info_by_goods_id) <= 8:
                    read_goods.description = "YOUR NEW TEXT"
                    db.session.commit()
                else:
                    return jsonify({"message": "You have not access to edit: "}, 403)

            read_user.login = "YOUR NEW TEXT"
            db.session.commit()
            return jsonify({"message": "Goods was updated"}, 200)
        else:
            return jsonify({"message": "Invalid input"}, 404)

    def delete_goods_from_db(self, id_of_g=None, tag=None, user_id=None):
        # delete goods from db by his `id`
        if id_of_g:
            delete_goods = Goods.query.get(id_of_g)
            delete_purchase = Purchase.query.filter_by(text=tag).first()
            db.session.delete(delete_goods)
            db.session.delete(delete_purchase)
            db.session.commit()
            return jsonify({"message": "Goods was deleted"}, 200)
        else:
            return jsonify({"message": "Goods wont deleted"}, 404)


# User Controller
class UserController(object):
    def __init__(self, model_user=User()):
        self.model_user = model_user

    def create(self, user_data=None):
        self.model_user.login = user_data.get('login')
        self.model_user.password = user_data.get('password')
        self.model_user.username = user_data.get('name')
        user_from_db = User.query.filter_by(login=self.model_user.login).first()

        if not self.model_user.login or not self.model_user.password or not self.model_user.username:
            return jsonify({"message": "Invalid input"}, 400)
        elif user_from_db is not None:
            return jsonify({"message": "User exist with such login"}, 409)
        else:
            hash_pwd = generate_password_hash(self.model_user.password)
            data = User(self.model_user.login, hash_pwd, self.model_user.username)
            db.session.add(data)
            db.session.commit()
            return jsonify({"message": "User was created"}, 200)

    def read(self, idi=None):
        return self.model_user.read_from_db(idi=idi)

    def update(self, idi=None, login=None, password=None, username=None):
        return self.model_user.update_info(idi=idi, login=login, password=password, username=username)

    def delete(self, id_of_d=None):
        return self.model_user.delete_from_db(id_of_d=id_of_d)


# Goods Controller
class GoodsController(object):
    def __init__(self, model_goods=Goods()):
        self.model_goods = model_goods

    def create(self, goods_data=None):
        self.model_goods.tag = goods_data.get('tag')
        self.model_goods.description = goods_data.get('description')
        self.model_goods.price = goods_data.get('price')
        self.model_goods.amount = goods_data.get('amount')
        current_user = goods_data.get('login')

        customer = User.query.filter_by(login=current_user).first()

        if not self.model_goods.description or not self.model_goods.tag or not current_user:
            return jsonify({"message": "Invalid input"}, 400)
        elif customer is None:
            return jsonify({"message": " don't know "}, 409)
        else:
            data = Goods(self.model_goods.tag, self.model_goods.description,
                         self.model_goods.price, self.model_goods.amount, customer)

            Purchase(customer, data, goods_data.get('tag'))
            db.session.add(data)
            db.session.commit()
            return jsonify({"message": "Goods was created"}, 200)

    # by tag
    def all_goods(self, tag=None):
        return self.model_goods.read_by_tag(tag=tag)

    # by user_id
    def all_goods_by_user_id(self, user=None):
        return self.model_goods.read_by_user_id(user=user)

    def update_goods(self, goods_data=None):
        return self.model_goods.goods_update(goods_data=goods_data)

    def delete(self, id_of_g=None, tag=None, user_id=None):
        return self.model_goods.delete_goods_from_db(id_of_g=id_of_g, tag=tag, user_id=user_id)


@app.route('/api/v1/hello-world-6')
def hello_world():
    # return "Hello World! Варіант 6"
    return render_template("index.html")


def check_for_token(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['id']).first()

        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return wrapped


# use POSTMAN post
# http://127.0.0.1:5000/UserCreate?login=Nazar&password=1111&name=naz123
@app.route('/UserCreate', methods=['POST'])
def create_user():
    user_controller = UserController()
    user_data = request.args
    return user_controller.create(user_data)


@app.route('/log_in', methods=['GET'])
def login():
    data = request.authorization

    if not data or not data.username or not data.password:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    user = User.query.filter_by(username=data.username).first()
    if not user:
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})

    if check_password_hash(user.password, data.password):
        token = jwt.encode({'id': user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=25)},
                           app.config['SECRET_KEY'])

        return jsonify({'token': token.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


# http://127.0.0.1:5000/UserView
@app.route('/UserView', methods=['GET'])
@check_for_token
def read_user(current_user):
    return UserController().read(current_user.id)


# http://127.0.0.1:5000/UserUpdate?id=1&login=Nazar&password=222&username=naz12
@app.route('/UserUpdate', methods=['PUT'])
@check_for_token
def update_user(current_user):
    idi = current_user.id
    new_login = request.args.get('login')
    new_password = request.args.get('password')
    new_username = request.args.get('username')
    return UserController().update(idi, new_login, new_password, new_username)


# http://127.0.0.1:5000/UserDelete?id=1
@app.route('/UserDelete', methods=['DELETE'])
@check_for_token
def delete_user(current_user):
    return UserController().delete(current_user.id)


# http://127.0.0.1:5000/GoodsCreate?tag=Mazda&description=This is electric car&price=43563262&amount=3&login=Nazar
@app.route('/GoodsCreate', methods=['POST'])
def create_goods():
    goods_data = request.args
    return GoodsController().create(goods_data)


# http://127.0.0.1:5000/GoodsByTag?tag=Mazda
@app.route('/GoodsByTag', methods=['GET'])
@check_for_token
def goods_by_tag(current_user):
    tag_data = request.args.get('tag')
    read_goods = GoodsController().all_goods(tag_data)
    return read_goods


# http://127.0.0.1:5000/GoodsByUser
@app.route('/GoodsByUser', methods=['GET'])
@check_for_token
def goods_by_user(current_user):
    read_goods = GoodsController().all_goods_by_user_id(current_user.id)
    return read_goods


# http://127.0.0.1:5000/GoodsUpdate?user_id=1&goods_id=1
@app.route('/GoodsUpdate', methods=['PUT'])
def update_goods():
    goods_data = request.args
    return GoodsController().update_goods(goods_data)


# http://127.0.0.1:5000/GoodsDelete?id=1&tag=Mazda
@app.route('/GoodsDelete', methods=['DELETE'])
@check_for_token
def delete_goods(current_user):
    identifier = request.args.get('id')
    current_tag = request.args.get('tag')
    customer = current_user.id
    return GoodsController().delete(identifier, current_tag, customer)


if __name__ == '__main__':
    # app.run()
    manager.run()
