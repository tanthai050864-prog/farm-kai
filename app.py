from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "smartfarm"

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "farm.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==========================
# MODEL
# ==========================
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


# ==========================
# CREATE CAGES
# ==========================
def create_cages():
    names = []

    for i in range(1, 213):
        names.append(f"F{i:03}")

    for i in range(1, 293):
        names.append(f"K{i:03}")

    for i in range(1, 101):
        names.append(f"BH{i:03}")

    for name in names:
        if not Cage.query.filter_by(cage=name).first():
            db.session.add(Cage(cage=name))

    db.session.commit()


# ==========================
# LOGIN
# ==========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        if request.form["password"] == "FW100":
            session["logged"] = True
            return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ==========================
# HOME
# ==========================
@app.route("/")
def home():

    if not session.get("logged"):
        return redirect("/login")

    return render_template("index.html")


# ==========================
# REGISTER
# ==========================
@app.route("/register", methods=["GET", "POST"])
def register():

    if not session.get("logged"):
        return redirect("/login")

    if request.method == "POST":

        cage = Cage(
            customer=request.form["customer"],
            mother=request.form["mother"],
            father=request.form["father"],
            phone=request.form["phone"]
        )

        db.session.add(cage)
        db.session.commit()

        return redirect("/manage")

    return render_template("register.html")


# ==========================
# MANAGE
# ==========================
@app.route("/manage")
def manage():

    if not session.get("logged"):
        return redirect("/login")

    waiting = Cage.query.filter(Cage.cage == None).all()
    cages = Cage.query.filter(Cage.cage != None).all()

    cage_map = {c.cage: c.customer for c in cages}

    return render_template(
        "manage.html",
        waiting=waiting,
        cages=cage_map
    )


# ==========================
# ASSIGN
# ==========================
@app.route("/assign/<int:i>/<cage>")
def assign(i, cage):

    waiting = Cage.query.filter(Cage.cage == None).all()

    if i < len(waiting):
        waiting[i].cage = cage
        db.session.commit()

    return redirect("/manage")


# ==========================
# ZONES
# ==========================
@app.route("/zones")
def zones():

    if not session.get("logged"):
        return redirect("/login")

    return render_template("zones.html")


@app.route("/zone/<z>")
def zone(z):

    cages = Cage.query.filter(
        Cage.cage.startswith(z.upper())
    ).all()

    return render_template(
        "cages.html",
        cages=cages,
        title=z.upper()
    )


# ==========================
# STATUS
# ==========================
@app.route("/status/<cage>")
def status(cage):

    data = Cage.query.filter_by(cage=cage).first()

    if not data:
        return redirect("/zones")

    status_data = json.loads(data.status or "{}")

    return render_template(
        "status.html",
        cage=cage,
        data={
            "customer": data.customer,
            "mother": data.mother,
            "father": data.father,
            "phone": data.phone,
            "eggs": data.eggs,
            "finish_date": data.finish_date,
            "status": status_data
        },
        days=1,
        stage="1-2"
    )


# ==========================
# UPDATE
# ==========================
@app.route("/update/<cage>", methods=["GET", "POST"])
def update(cage):

    data = Cage.query.filter_by(cage=cage).first()

    if request.method == "POST":

        status = {
            "eggs": request.form.get("eggs", 0),
            "note": request.form.get("note", ""),
            "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
        }

        data.eggs = int(status["eggs"])
        data.status = json.dumps(status)

        history = json.loads(data.history or "[]")
        history.append(status)

        data.history = json.dumps(history)

        db.session.commit()

        return redirect(f"/status/{cage}")

    return render_template(
        "update.html",
        cage=cage,
        data=data
    )


# ==========================
# HISTORY
# ==========================
@app.route("/history/<cage>")
def history(cage):

    data = Cage.query.filter_by(cage=cage).first()

    return render_template(
        "history.html",
        cage=cage,
        history=json.loads(data.history or "[]")
    )


# ==========================
# FINISH
# ==========================
@app.route("/finish/<cage>")
def finish(cage):

    data = Cage.query.filter_by(cage=cage).first()

    if data:
        data.finish_date = datetime.now().strftime("%d/%m/%Y")
        db.session.commit()

    return redirect("/zones")


# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_cages()

    app.run(host="0.0.0.0", port=5000, debug=True)