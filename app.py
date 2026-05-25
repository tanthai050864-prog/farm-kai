from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

app = Flask(__name__)

waiting = []
customers = []
finished = []
chicks_born = 0
cages = {}

# F
for i in range(1, 213):
    cages[f'F{i:03}'] = None

# K
for i in range(1, 293):
    cages[f'K{i:03}'] = None

# BH
for i in range(1, 101):
    cages[f'BH{i:03}'] = None


# ---------------------------
# ALERT
# ---------------------------
def check_alert(status):

    if not status:
        return None

    brooding = status.get("brooding")

    if not brooding:
        return None

    try:
        d, m, y = map(int, brooding.split("/"))

        if y > 2500:
            y -= 543

        due = datetime(y, m, d) + timedelta(days=10)
        diff = (due - datetime.now()).days

        if diff <= 0:
            return "ถึงกำหนด"

        return f"อีก {diff} วัน"

    except:
        return None


# ---------------------------
# STAGE
# ---------------------------
def get_stage(data):

    if not data:
        return "1-2", 1

    inject = data.get("status", {}).get("inject_date")

    if not inject:
        return "1-2", 1

    try:
        d, m, y = map(int, inject.split("/"))

        if y > 2500:
            y -= 543

        start = datetime(y, m, d)
        days = (datetime.now() - start).days + 1

        if days <= 14:
            return "1-2", days
        elif days <= 28:
            return "3-4", days
        elif days <= 56:
            return "5-8", days
        elif days <= 84:
            return "9-12", days
        else:
            return "kpi", days

    except:
        return "1-2", 1


# ---------------------------
# HOME
# ---------------------------
@app.route('/')
def home():
    return render_template("index.html")


# ---------------------------
# REGISTER
# ---------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "POST":
        data = request.form.to_dict()
        waiting.append(data)
        customers.append(data)
        return redirect('/manage')

    return render_template("register.html")


# ---------------------------
# MANAGE
# ---------------------------
@app.route('/manage')
def manage():
    return render_template("manage.html", waiting=waiting, cages=cages)


# ---------------------------
# ASSIGN
# ---------------------------
@app.route('/assign/<int:i>/<cage>')
def assign(i, cage):

    if cages.get(cage) is None and i < len(waiting):

        cages[cage] = waiting.pop(i)

        if not isinstance(cages[cage].get("status"), dict):
            cages[cage]["status"] = {}

        if not isinstance(cages[cage].get("history"), list):
            cages[cage]["history"] = []

    return redirect('/manage')


# ---------------------------
# ZONES
# ---------------------------
@app.route('/zones')
def zones():
    return render_template("zones.html")


@app.route('/zone/<z>')
def zone(z):

    data = {
        k: v for k, v in cages.items()
        if k.startswith(z.upper())
    }

    for v in data.values():
        if v:
            v["alert"] = check_alert(v.get("status"))

    return render_template(
        "cages.html",
        groups={z: data},
        title=z
    )


# ---------------------------
# STATUS
# ---------------------------
@app.route('/status/<cage>')
def status(cage):

    data = cages.get(cage)

    if not data:
        return redirect('/zones')

    if not isinstance(data.get("status"), dict):
        data["status"] = {}

    if not isinstance(data.get("history"), list):
        data["history"] = []

    stage, days = get_stage(data)

    return render_template(
        "status.html",
        cage=cage,
        data=data,
        stage=stage,
        days=days
    )


# ---------------------------
# UPDATE
# ---------------------------
@app.route('/update/<cage>', methods=['GET', 'POST'])
def update(cage):

    global chicks_born

    if cages.get(cage) is None:
        return redirect('/zones')

    if request.method == "POST":

        status_data = request.form.to_dict()
        status_data["updated_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")

        if not isinstance(cages[cage].get("status"), dict):
            cages[cage]["status"] = {}

        if not isinstance(cages[cage].get("history"), list):
            cages[cage]["history"] = []

        cages[cage]["status"] = status_data
        cages[cage]["history"].append(status_data)

        try:
            chicks_born += int(status_data.get("eggs", 0))
        except:
            pass

        return redirect(f'/status/{cage}')

    return render_template(
        "update.html",
        cage=cage,
        data=cages[cage]
    )


# ---------------------------
# HISTORY
# ---------------------------
@app.route('/history/<cage>')
def history(cage):

    return render_template(
        "history.html",
        cage=cage,
        history=cages[cage]["history"]
    )


# ---------------------------
# FINISH
# ---------------------------
@app.route('/finish/<cage>')
def finish(cage):

    if cages.get(cage):
        cages[cage]["finish_date"] = datetime.now().strftime("%d/%m/%Y")
        finished.append(cages[cage])
        cages[cage] = None

    return redirect('/zones')


# ---------------------------
# DASHBOARD
# ---------------------------
@app.route('/dashboard')
def dashboard():

    return render_template(
        "dashboard.html",
        customers=len(customers),
        born=chicks_born
    )


@app.route('/history_all')
def history_all():
    return render_template("history_all.html")


@app.route('/history_in')
def history_in():
    return render_template(
        "history_in.html",
        customers=customers
    )


@app.route('/history_out')
def history_out():
    return render_template(
        "history_out.html",
        done=finished
    )


@app.route('/farm')
def farm():
    return render_template("farm.html")


# ---------------------------
# RUN
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)