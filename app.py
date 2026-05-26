from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///farm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# -------------------
# MODEL
# -------------------
class Cage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cage = db.Column(db.String(20), unique=True)
    customer = db.Column(db.String(100))
    mother = db.Column(db.String(100))
    father = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    eggs = db.Column(db.Integer, default=0)
    status = db.Column(db.Text, default="{}")
    history = db.Column(db.Text, default="[]")
    finish_date = db.Column(db.String(50))


# -------------------
# CREATE CAGES
# -------------------
def create_cages():
    all_cages = []

    for i in range(1,213):
        all_cages.append(f"F{i:03}")

    for i in range(1,293):
        all_cages.append(f"K{i:03}")

    for i in range(1,101):
        all_cages.append(f"BH{i:03}")

    for cage_name in all_cages:
        if not Cage.query.filter_by(cage=cage_name).first():
            db.session.add(Cage(cage=cage_name))

    db.session.commit()


# -------------------
# HOME
# -------------------
@app.route('/')
def home():
    return render_template("index.html")


# -------------------
# REGISTER
# -------------------
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == "POST":

        empty = Cage.query.filter_by(customer=None).first()

        if empty:
            empty.customer = request.form['customer']
            empty.mother = request.form['mother']
            empty.father = request.form['father']
            empty.phone = request.form['phone']

            db.session.commit()

        return redirect('/zones')

    return render_template("register.html")


# -------------------
# ZONES
# -------------------
@app.route('/zones')
def zones():
    return render_template("zones.html")


@app.route('/zone/<z>')
def zone(z):

    cages = Cage.query.filter(
        Cage.cage.startswith(z.upper())
    ).all()

    return render_template(
        "cages.html",
        cages=cages,
        title=z
    )


# -------------------
# STATUS
# -------------------
@app.route('/status/<cage>')
def status(cage):

    data = Cage.query.filter_by(cage=cage).first()

    if not data:
        return redirect('/zones')

    return render_template(
        "status.html",
        cage=cage,
        data=data
    )


# -------------------
# UPDATE
# -------------------
@app.route('/update/<cage>', methods=['GET','POST'])
def update(cage):

    data = Cage.query.filter_by(cage=cage).first()

    if request.method == "POST":

        status = {
            "eggs": request.form['eggs'],
            "note": request.form['note'],
            "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
        }

        data.eggs = int(request.form['eggs'])
        data.status = json.dumps(status)

        hist = json.loads(data.history)
        hist.append(status)

        data.history = json.dumps(hist)

        db.session.commit()

        return redirect(f'/status/{cage}')

    return render_template(
        "update.html",
        cage=cage,
        data=data
    )


# -------------------
# HISTORY
# -------------------
@app.route('/history/<cage>')
def history(cage):

    data = Cage.query.filter_by(cage=cage).first()

    return render_template(
        "history.html",
        cage=cage,
        history=json.loads(data.history)
    )


# -------------------
# FINISH
# -------------------
@app.route('/finish/<cage>')
def finish(cage):

    data = Cage.query.filter_by(cage=cage).first()

    data.finish_date = datetime.now().strftime("%d/%m/%Y")

    db.session.commit()

    return redirect('/zones')


# -------------------
# RUN
# -------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_cages()

    app.run(debug=True)