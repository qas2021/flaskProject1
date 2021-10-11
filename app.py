from flask import Flask, request, jsonify, make_response
from flask_bcrypt import Bcrypt
from datetime import datetime
from sqlalchemy import create_engine
import re
from flask_sqlalchemy import SQLAlchemy
# from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields
import pymysql

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://qasim:Qwer_1234-@localhost/lostnfound'
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqldb://root:root@db:3306/jado"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


def regex(pswd):
    if len(pswd) < 8:
        return 'password must be atleast 8 characters long!'
    elif re.search(r'[!@#$%&]', pswd) is None:
        return 'password must contain atlest one special symbol i.e !@#$%&'
    elif re.search(r'\d', pswd) is None:
        return 'password ust contain atleast one digit'
    elif re.search('[A-Z]', pswd) is None:
        return 'password must contain one capital alphabet'
    elif re.match(r'[a-z A-Z 0-9 !@#$%&]{8}', pswd):
        return 0


### Models ####
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


class data(db.Model):
    __tablename__ = "data"
    id = db.Column(db.String(20), primary_key=True)
    item_name = db.Column(db.String(20))
    location = db.Column(db.String(100))
    description = db.Column(db.String(200))
    date = db.Column(db.String(20))
    datai = db.Column(db.LargeBinary)

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, name, loc, des, datee, dataa, id):
        self.id = id
        self.item_name = name
        self.location = loc
        self.description = des
        self.date = datee
        self.datai = dataa

    def __repr__(self):
        return '' % self.id


db.create_all()


@app.route('/search', methods=['POST'])
def search():
    loc = request.form['loc']
    name = request.form['name']
    missing = data.query.filter_by(item_name=name).filter_by(location=loc).first()
    if missing is None:
        return "No such item"
    else:

        # id = db.Column(db.String(20), primary_key=True)
        # item_name = db.Column(db.String(20))
        # location = db.Column(db.String(100))
        # description = db.Column(db.String(200))
        # date = db.Column(db.String(20))
        # datai = db.Column(db.LargeBinary)
        #
        data_ = []
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        bookmark = data.query.filter_by(item_name=name).filter_by(location=loc).paginate(page=page, per_page=per_page, error_out= True)
        for book in bookmark.items:
            data_.append({
                'id': book.id,
                'item_name': book.item_name,
                'location': book.location,
                'description': book.description,
                'date': book.date,
                # 'img': book.datai
            })
        meta = {
            'page': bookmark.page,
            'pages': bookmark.pages,
            'total_count': bookmark.total,
            'prev_page': bookmark.prev_num,
            'next_page': bookmark.next_num,
            'has_next': bookmark.has_next,
            'has_prev': bookmark.has_prev

        }
        return jsonify({'data': data_, 'meta': meta})


@app.route('/update', methods=['POST'])
def update_state():
    loc = request.form['loc']
    name = request.form['name']
    idd = request.form['id']
    img = request.files['img']
    nloc = request.form['nloc']
    des = request.form['description']
    tareekh = request.form['date']
    newname = request.form['nname']

    try:
        value = data.query.filter_by(item_name=name).filter_by(location=loc).first()
        value.id = str(idd)
        value.item_name = str(newname)
        value.location = str(nloc)
        value.description = str(des)
        value.date = str(tareekh)
        value.datai = img.read()

        db.session.flush()
        db.session.commit()
        return "updated"
    except:
        return 'Error in def update_state'


@app.route('/delete', methods=['POST'])
def delete():
    loc = request.form['loc']
    name = request.form['name']
    missingg = data.query.filter_by(item_name=name).filter_by(location=loc).first()
    if missingg is None:
        return "No such item"
    else:
        data.query.filter_by(item_name=name).filter_by(location=loc).delete()
        db.session.commit()
        check = data.query.filter_by(item_name=name).filter_by(location=loc).first()
        if check is None:
            return "record deleted"
        else:
            return "Not deleted yet"


@app.route('/insert', methods=["POST"])
def insert():
    idd = request.form['id']
    img = request.files['img']
    loc = request.form['loc']
    des = request.form['description']
    tareekh = request.form['date']
    name = request.form['name']
    inserted = data(name, loc, des, tareekh, img.read(), idd)
    db.session.add(inserted)
    db.session.commit()
    return "data added successfully WHERE IMAGE= " + img.name


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
    app.run(debug=True)
