from flask import Flask, render_template
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime

# instantiate the app
app = Flask(__name__)
# app config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# instantiate db
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@app.route('/api/v1/hello-world-6')
def hello_world():
    # return "Hello World! Варіант 6"
    return render_template("index.html")


customers = db.Table('customers',
                     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('goods_id', db.Integer, db.ForeignKey('goods.id'))
                     )


class Goods(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)

    # every goods has its customer
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # one-to-one (one statistics - one goods)
    goods_statistics = db.relationship('Statistics', backref='goods', uselist=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)

    # one-to-many (one user - many goods)
    users_goods = db.relationship('Goods', backref='customer')

    # many-to-many (two or more users don't have permission for sell the product)
    permissions_for_sell = db.relationship('Goods', secondary=customers,
                                           backref=db.backref('customers', lazy='dynamic'))


class Statistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)

    # every statistics has one goods
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'))


if __name__ == "__main__":
    # app.run(debug=True)
    manager.run()
