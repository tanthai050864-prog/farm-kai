from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, "farm.db")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ============================
# MODEL
# ============================
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


# ============================
# CREATE CAGES
# ============================
def create_cages():

    names = []

    for i in range(1, 213):
        names.append(f"F{i:03}")

    for i in range(1, 293):
        names.append(f"K{i:03}")

    for i in range(1, 101):
        names.append(f"BH{i:03}")

    for n in names:
        if not Cage.query.filter_by(cage=n).first():
            db.session.add(Cage(cage=n))

    db.session.commit()


# ============================
# HOME
# ============================
@app.route("/")
def home():
    return render_template("index.html")


# ============================
# REGISTER
# ============================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        empty = Cage.query.filter_by(customer=None).first()

        if empty:
            empty.customer = request.form["customer"]
            empty.mother = request.form["mother"]
            empty.father = request.form["father"]
            empty.phone = request.form["phone"]

            db.session.commit()

        return redirect("/zones")

    return render_template("register.html")


# ============================
# ZONES
# ============================
@app.route("/zones")
def zones():
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


# ============================
# STATUS
# ============================
@app.route("/status/<cage>")
def status(cage):

    data = Cage.query.filter_by(cage=cage).first()

    if not data:
        return redirect("/zones")

    # FIX JSON
    status_data = {}
    try:
        status_data = json.loads(data.status)
    except:
        status_data = {}

    history_data = []
    try:
        history_data = json.loads(data.history)
    except:
        history_data = []

    return render_template(
        "status.html",
        cage=cage,
        data={
            "customer": data.customer,
            "mother": data.mother,
            "father": data.father,
            "phone": data.phone,
            "eggs": data.eggs,
            "status": status_data,
            "history": history_data
        }
    )


# ============================
# UPDATE
# ============================
@app.route("/update/<cage>", methods=["GET", "POST"])
def update(cage):

    data = Cage.query.filter_by(cage=cage).first()

    if not data:
        return redirect("/zones")

    if request.method == "POST":

        status = {
            "eggs": request.form.get("eggs", 0),
            "note": request.form.get("note", ""),
            "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
        }

        data.eggs = int(status["eggs"])
        data.status = json.dumps(status)

        try:
            hist = json.loads(data.history)
        except:
            hist = []

        hist.append(status)
        data.history = json.dumps(hist)

        db.session.commit()

        return redirect(f"/status/{cage}")

    return render_template(
        "update.html",
        cage=cage,
        data=data
    )


# ============================
# HISTORY
# ============================
@app.route("/history/<cage>")
def history(cage):

    data = Cage.query.filter_by(cage=cage).first()

    if not data:
        return redirect("/zones")

    try:
        history_data = json.loads(data.history)
    except:
        history_data = []

    return render_template(
        "history.html",
        cage=cage,
        history=history_data
    )


# ============================
# FINISH
# ============================
@app.route("/finish/<cage>")
def finish(cage):

    data = Cage.query.filter_by(cage=cage).first()

    if data:
        data.finish_date = datetime.now().strftime("%d/%m/%Y")
        db.session.commit()

    return redirect("/zones")


# ============================
# RUN
# ============================
if __name__ == "__main__":

    with app.app_context():
        db.create_all()
        create_cages()

    app.run(host="0.0.0.0", port=5000, debug=True)