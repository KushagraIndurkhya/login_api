from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os


app = Flask(__name__)

currentDirectory = os.getcwd()
databasePath = os.path.join(currentDirectory,"database.db")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+databasePath
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64),index=True,unique=True)
    email = db.Column(db.String(120),index=True,unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def getJsonData(self):
        return {"username": self.username,
                "email": self.email}

if not os.path.exists(databasePath):
    db.create_all()

@app.route('/', methods=['GET','POST'])
def home():
    return ""

@app.route('/signup',methods = ['POST', 'GET'])
def signup():
   user_name = request.form.get('name')
   user_email = request.form.get('email')
   user_pass=request.form.get('password')
   if not user_name or not user_pass or not user_email:
       return jsonify({"status": {"type": "failure", "message": "missing data"}})
   if User.query.filter_by(username=user_name).first():
       return jsonify({"status": {"type": "failure", "message": "username already exists"}})
   if User.query.filter_by(email=user_email).first():
       return jsonify({"status": {"type": "failure", "message": "email already exists"}})
   u=User()
   u.username=user_name
   u.email=user_email
   u.password_hash=generate_password_hash(user_pass)
   db.session.add(u)
   db.session.commit()
   # return "signup successful"
   user = User.query.filter_by(username=user_name).first()
   return jsonify({"status": {"type": "success", "message": "Signup Successful","data" : user.getJsonData()}})


@app.route("/login", methods=["GET","POST"])
def login():
    username= request.form.get("username")
    password= request.form.get("password")

    if not username or not password:
        return jsonify({"status": {"type": "failure", "message": "Missing Data"}})
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password) :
        msg = {"status" : { "type" : "failure" ,   "message" : "Username or password incorrect"}}

    else:
        msg = {"status" : { "type" : "success" ,
                             "message" : "You logged in"} ,
               "data" : {"user" : user.getJsonData() }
        }

        # return "logged in"

    return jsonify(msg)


if __name__ == '__main__':
    app.run()
