from flask import Flask, flash, redirect,render_template,request, session, url_for
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///tracker.db"
app.secret_key = 'super secret key'
db = SQLAlchemy(app)

class trackers(db.Model):
   id = db.Column('tracker_id', db.Integer, primary_key = True)
   name = db.Column(db.String(100))
   description = db.Column(db.String(50))  
   datatype = db.Column(db.String(200))
   settings = db.Column(db.String(50))
   user_id = db.Column(db.String(50))

def __init__(self, name, description, datatype,settings,user_id):
   self.name = name
   self.description = description
   self.datatype = datatype
   self.settings = settings
   self.user_id = user_id

class log(db.Model):
    id = db.Column('log_id', db.Integer, primary_key = True)
    tracker_id = db.Column(db.String(100))
    user_id = db.Column(db.String(100))
    value = db.Column(db.String(50))  
    date = db.Column(db.String(50))
    note = db.Column(db.String(50))

    def __init__(self,tracker_id,user_id,value,date,note):
        self.tracker_id = tracker_id
        self.user_id = user_id
        self.value = value
        self.date = date 
        self.note = note

class User(db.Model):
    id=db.Column('user_id',db.Integer,primary_key = True)
    name=db.Column(db.String(50))
    username=db.Column(db.String(50))
    password=db.Column(db.String(8))

    def __init__(self,name,username,password):
        self.name = name
        self.username = username
        self.password = password


@app.route("/")
def home():
    if(session.get('username')):
        return render_template("index.html", trackers_db=trackers.query.filter_by(user_id=session['username']).all())
    else:
        return render_template("login.html")


@app.route('/login', methods=['GET','POST'])
def login():
    if(request.method == 'POST'):
        if not request.form['username'] or not request.form['password']:
            flash('Please enter all the fields', 'error')
        else:
            data = User.query.filter_by(username = request.form['username']).all()
            if(len(data))>0:
                print('succes')
                session['username']=request.form['username']
                return redirect(url_for('home'))
            else:
                print('failed')
                # flash('Record was successfully added')
                return redirect(url_for('login'))
    return render_template('/login.html')


@app.route('/signin',methods=['GET','POST'])
def signin():
    if request.method == 'POST':
        if not request.form['username'] or not request.form['password'] or not request.form['name']:
            flash('Please enter all the fields', 'error')

        else:
            data = User(name=request.form['name'],username = request.form['username'],password=request.form['password'])
            db.session.add(data)
            db.session.commit()
            session['username']=request.form['username']
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

@app.route('/signout')
def signout():
    session['username']=''
    return redirect(url_for('login'))
    

@app.route('/tracker_log/<int:id>',methods=['GET','POST'])
def tracker_log(id):
    if request.method == 'GET':
        args = request.args
        data = trackers.query.filter_by(id = id).first()
        log_q = log.query.filter_by(tracker_id= id,user_id=session['username']).all()
        print(data)
        dates = []
        values = []
        import matplotlib.pyplot as plt
        from matplotlib import style
        style.use('fivethirtyeight')
        from dateutil import parser
        for row in log_q:
            dates.append(parser.parse(row.date))
            values.append(row.value)
        fig = plt.figure(figsize=(18, 8))
        plt.plot_date(dates, values, '-')
        plt.xlabel('Date and Time')
        plt.ylabel('Values')
        plt.tight_layout()
        plt.savefig('static/graph.png')
        if(data and data.settings):
            opts = data.settings
            opts = opts.split(',')
        else:
            opts = ''
        return render_template('tracker_log.html', tracker=data,logs=log_q,opts=opts)
    else:
        if(not request.form['value'] or not request.form['date'] or not request.form['note']):
            flash('Please enter all the fields', 'error')
        else:
            data = log(tracker_id=request.form['tracker_name'],value=request.form['value'],date=request.form['date'],user_id=session['username'],note=request.form['note'])
            db.session.add(data)
            db.session.commit()
        return redirect(url_for('tracker_log',id=request.form['tracker_name']))

@app.route('/addTracker', methods=['GET','POST'])
def addTracker():
    if request.method=='POST':
        name = request.form['name']
        desc = request.form['desc']
        type = request.form['type']
        if not name or not desc or not type:
            flash('Please enter all the fields', 'error')
            return render_template('addTracker.html',edit=False)      
        else:
            data = trackers(name=name, description=desc, datatype=type, settings=request.form['choices'], user_id=session['username'])
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('home'))
    else:
        return render_template('addTracker.html')

@app.route('/tracker_edit/<int:id>', methods=['GET','POST'])
def editTracker(id):
    data = trackers.query.filter_by(id=id).first()
    if request.method == 'POST':
        dname = request.form['name']
        desc = request.form['desc']
        type = request.form['type']
        settings=request.form['choices']
        if not dname or not desc or not type:
            flash('Please enter all the fields', 'error')
            return render_template('addTracker.html',tracker=data,edit=True)
        else:
            data.name = dname
            data.description = desc
            data.datatype = type
            data.settings = settings
            db.session.commit()
            return redirect(url_for('home'))
    else:
        return render_template('addTracker.html',tracker=data,edit=True)

@app.route('/tracker_delete/<int:id>')
def deleteTracker(id):
    trackers.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/back')
def back():
    return redirect(url_for('home'))    

@app.route('/tracker_log_edit/<int:trckr_id>/<int:id>', methods=['GET','POST'])
def editLog(trckr_id,id):
    data = log.query.filter_by(id=id).first()
    data2 = trackers.query.filter_by(id=trckr_id).first()
    log_q = log.query.filter_by(tracker_id= trckr_id,user_id=session['username']).all()
    logs = []
    for l in log_q:
        if l.value != data.value and l.date != data.date:
            logs.append(l)
    if(data2 and data2.settings):
        opts = data2.settings
        opts = opts.split(',')
    else:
        opts = ''
    if request.method == 'POST':
        if(not request.form['value'] or not request.form['date'] or not request.form['note']):
            flash('Please enter all the fields', 'error')
        else:
            data.tracker_id=request.form['tracker_name']
            data.value=request.form['value']
            data.date=request.form['date']
            data.user_id=session['username']
            data.note=request.form['note']
            db.session.commit()
        return redirect(url_for('tracker_log',id = request.form['tracker_name']))
    else:
        return render_template('tracker_log.html',edit = True,tracker = data2,log=data,logs = logs)

@app.route('/tracker_log_delete/<int:trckr_id>/<int:id>')
def logDelete(trckr_id,id):
    log.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect(url_for('tracker_log',id=trckr_id))

if __name__ == "__main__":
    db.create_all()
    app.run(host = '0.0.0.0',debug = True)     