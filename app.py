```python
from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

app = Flask(__name__)

waiting=[]
customers=[]
finished=[]
chicks_born=0
cages={}

for i in range(1,213):
    cages[f'F{i:03}']=None

for i in range(1,293):
    cages[f'K{i:03}']=None

app.config['SEND_FILE_MAX_AGE_DEFAULT']=0


@app.after_request
def no_cache(response):
    response.headers["Cache-Control"]="no-store, no-cache, must-revalidate, max-age=0"
    return response


def check_alert(status):

    if not status:
        return None

    brooding=status.get("brooding")

    if not brooding:
        return None

    try:
        d,m,y=map(int,brooding.split("/"))

        if y>2500:
            y-=543

        due=datetime(y,m,d)+timedelta(days=10)
        diff=(due-datetime.now()).days

        if diff<=0:
            return "🔔 ถึงกำหนดเช็คเชื้อแล้ว"

        return f"⏳ อีก {diff} วัน"

    except:
        return None


def get_stage(data):

    if not data:
        return "1-2",1

    inject=data.get("status",{}).get("inject_date")

    if not inject:
        return "1-2",1

    try:
        d,m,y=map(int,inject.split("/"))

        if y>2500:
            y-=543

        start=datetime(y,m,d)

        days=(datetime.now()-start).days+1

        if days<=14:
            return "1-2",days
        elif days<=28:
            return "3-4",days
        elif days<=56:
            return "5-8",days
        elif days<=84:
            return "9-12",days
        else:
            return "kpi",days

    except:
        return "1-2",1


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register',methods=['GET','POST'])
def register():

    if request.method=="POST":
        data=request.form.to_dict()
        waiting.append(data)
        customers.append(data)
        return redirect('/manage')

    return render_template("register.html")


@app.route('/manage')
def manage():
    return render_template("manage.html",waiting=waiting,cages=cages)


@app.route('/assign/<int:i>/<cage>')
def assign(i,cage):

    if cages[cage] is None and i<len(waiting):

        cages[cage]=waiting.pop(i)
        cages[cage]["status"]={}
        cages[cage]["history"]=[]
        cages[cage]["assigned_date"]=datetime.now()

    return redirect('/manage')


@app.route('/zones')
def zones():
    return render_template("zones.html")


@app.route('/zone/<z>')
def zone(z):

    data={k:v for k,v in cages.items() if k.startswith(z.upper())}

    for v in data.values():
        if v:
            v["alert"]=check_alert(v.get("status"))

    return render_template("cages.html",groups={z:data},title=z)


@app.route('/update/<cage>',methods=['GET','POST'])
def update(cage):

    global chicks_born

    if cages[cage] is None:
        return redirect('/zones')

    if request.method=="POST":

        status=request.form.to_dict()
        status["updated_at"]=datetime.now().strftime("%d/%m/%Y %H:%M")

        cages[cage]["status"]=status
        cages[cage]["history"].append(status)

        try:
            chicks_born+=int(status.get("eggs",0))
        except:
            pass

        return redirect('/zones')

    return render_template("update.html",cage=cage,data=cages[cage])


@app.route('/status/<cage>')
def status(cage):

    data=cages.get(cage)

    if not data:
        return redirect('/zones')

    stage,days=get_stage(data)

    return render_template(
        "status.html",
        cage=cage,
        data=data,
        stage=stage,
        days=days
    )


@app.route('/history/<cage>')
def history(cage):
    return render_template(
        "history.html",
        cage=cage,
        history=cages[cage]["history"]
    )


@app.route('/finish/<cage>')
def finish(cage):

    if cages[cage]:
        finished.append(cages[cage])
        cages[cage]=None

    return redirect('/zones')


@app.route('/dashboard')
def dashboard():

    return render_template(
        "dashboard.html",
        customers=len(customers),
        born=chicks_born
    )


if __name__=="__main__":
    app.run(debug=True)
```
