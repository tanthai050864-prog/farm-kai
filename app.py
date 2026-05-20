from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY']="smartfarm"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///farm.db'

db=SQLAlchemy(app)

login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(50))
    role=db.Column(db.String(20))


class Cage(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    cage=db.Column(db.String(20),unique=True)
    customer=db.Column(db.String(100))
    mother=db.Column(db.String(100))
    father=db.Column(db.String(100))
    eggs=db.Column(db.Integer,default=0)
    updated=db.Column(db.String(50))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="POST":
        u=User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if u:
            login_user(u)
            return redirect('/')

    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route('/')
@login_required
def home():
    return render_template("index.html")


@app.route('/update/<cage>',methods=['POST'])
@login_required
def update(cage):

    c=Cage.query.filter_by(cage=cage).first()

    c.eggs=request.form['eggs']
    c.updated=datetime.now().strftime("%d/%m/%Y %H:%M")

    db.session.commit()

    return redirect('/')


if __name__=="__main__":
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            db.session.add(
                User(
                    username="admin",
                    password="1234",
                    role="admin"
                )
            )
            db.session.commit()

    app.run(debug=True)