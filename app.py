from flask import Flask, render_template, request, redirect
from datetime import datetime, timedelta

app = Flask(__name__)

waiting=[]
customers=[]
finished=[]
chicks_born=0
returned=0
cages={}

for i in range(1,213):
    cages[f'F{i:03}']=None

for i in range(1,293):
    cages[f'K{i:03}']=None


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
        return f"⏳ อีก {diff} วัน ถึงกำหนดเช็คเชื้อ"
    except:
        return None


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        data=request.form.to_dict()
        waiting.append(data)
        customers.append(data)
        return redirect('/manage')
    return render_template('register.html')


@app.route('/manage')
def manage():
    return render_template('manage.html',waiting=waiting,cages=cages)


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
    return render_template('zones.html')


@app.route('/zone/<z>')
def zone(z):

    if z.upper()=="F":
        return render_template("f_groups.html")

    data={k:v for k,v in cages.items() if k.startswith("K")}

    for v in data.values():
        if v:
            v["alert"]=check_alert(v.get("status"))

    return render_template("cages.html",groups={"โซน K":data},title="โซน K")


@app.route('/zone/f/<group>')
def f_group(group):

    data={k:v for k,v in cages.items() if k.startswith("F")}

    if group=="1":
        data={k:v for k,v in data.items() if int(k[1:])<=60}
        title="คอกที่ 1 • ผู้ดูแล นายA"

    elif group=="2":
        data={k:v for k,v in data.items() if 61<=int(k[1:])<=162}
        title="คอกที่ 2 • ผู้ดูแล นายB"

    else:
        data={k:v for k,v in data.items() if 163<=int(k[1:])<=212}
        title="คอกที่ 3 • ผู้ดูแล นายC"

    for v in data.values():
        if v:
            v["alert"]=check_alert(v.get("status"))

    return render_template("cages.html",groups={title:data},title=title)


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
    return render_template("status.html",cage=cage,data=cages[cage])


@app.route('/history/<cage>')
def history(cage):
    return render_template("history.html",cage=cage,history=cages[cage]["history"])


@app.route('/finish/<cage>')
def finish(cage):

    if cages[cage]:
        data=cages[cage]
        data["finish_date"]=datetime.now().strftime("%d/%m/%Y")
        finished.append(data)
        cages[cage]=None

    return redirect('/zones')


@app.route('/farm')
def farm():
    return render_template("farm.html")


@app.route('/dashboard')
def dashboard():

    passed=0
    warning=0
    failed=0
    now=datetime.now()

    for c in cages.values():
        if c and c.get("assigned_date"):
            days=(now-c["assigned_date"]).days

            if days<=79:
                passed+=1
            elif days<=89:
                warning+=1
            else:
                failed+=1

    return render_template(
        "dashboard.html",
        customers=len(customers),
        born=chicks_born,
        passed=passed,
        warning=warning,
        failed=failed
    )


@app.route('/history_all')
def history_all():
    return render_template("history_all.html")


@app.route('/history_in')
def history_in():
    return render_template("history_in.html",customers=customers)


@app.route('/history_out')
def history_out():
    return render_template("history_out.html",done=finished)


if __name__=="__main__":
    app.run(debug=True)