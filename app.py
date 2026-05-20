(เอา app.py ที่มึงมีอยู่ตอนนี้ทั้งหมดจากข้อความก่อนหน้า แล้วแทนเฉพาะส่วน `get_stage` กับ `/status` ด้วยอันนี้)

```python
def get_stage(data):

    if not data:
        return "1-2",1

    status=data.get("status",{})
    inject=status.get("inject_date")

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
        elif days<=90:
            return "kpi",days
        else:
            return "done",days

    except:
        return "1-2",1


@app.route('/status/<cage>')
def status(cage):

    data=cages.get(cage)

    if not data:
        return redirect('/zones')

    if "status" not in data:
        data["status"]={}

    stage,days=get_stage(data)

    return render_template(
        'status.html',
        cage=cage,
        data=data,
        stage=stage,
        days=days
    )
```
