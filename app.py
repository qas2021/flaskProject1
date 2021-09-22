from flask import Flask, request, jsonify, make_response
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine
import re
from flask_sqlalchemy import SQLAlchemy
# from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://qasim:Qwer_1234-@localhost/lostnfound'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

def regex(pswd):
    if len(pswd) < 8:
        return 'password must be atleast 8 characters long!'
    elif re.search(r'[!@#$%&]', pswd) is None:
        return 'password must contain atlest one special symbol i.e !@#$%&'
    elif re.search(r'\d', pswd) is None:
        return 'password ust contain atleast one digit'
    elif re.search('[A-Z]' , pswd) is None:
        return 'password must contain one capital alphabet'
    elif re.match(r'[a-z A-Z 0-9 !@#$%&]{8}',pswd):
        return 0



###Models####
class user(db.Model):
    __tablename__ = "user"
    id = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(60))
    email = db.Column(db.String(100), unique=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, id, email, fname, lname, password):
        self.id = id
        self.email = email
        self.fname = fname
        self.lname = lname
        self.password = password

    def __repr__(self):
        return '' % self.id


db.create_all()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/signup', methods=["POST"])
def signupp():  # put application's code here
    idd = request.form['id']
    missing = user.query.filter_by(id=idd).first()
    if missing is not None:
        return "id already exists"

    fnamee = request.form['fname']
    lnamee = request.form['lname']
    emaill = request.form['email']
    password = request.form['password']

    missingg = user.query.filter_by(email=emaill).first()
    if missingg is not None:
        return "email already exists enter a new email!!"
    text = regex(password)
    if text == 0:
        encrypted_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        person = user(idd, emaill, fnamee, lnamee, encrypted_pw)
        db.session.add(person)
        db.session.commit()
        return "Account created!"
    return text


@app.route('/login', methods=["POST"])
def loginn():
    em = request.form['email']
    pswd = request.form['password']


    missingg = user.query.filter_by(email=em).first()
    if missingg is None:
        # if not bcrypt.check_password_hash(pswd_hash, pswd):
        #     return "invalid email and password"
        return "Invalid email!"
    else:
        # missingg = user.query.filter_by(email=em).filter_by(password=pswd).first()
        pswd_hash = user.query.filter_by(email=em).first().password
        if not bcrypt.check_password_hash(pswd_hash, pswd):
            print(pswd_hash)
            return 'Invalid password!!'
        else:
            return 'You have been logged in successfully'


if __name__ == '__main__':
    app.run()
