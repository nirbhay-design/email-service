from flask import *
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'
db = SQLAlchemy(app)

class Userinfo(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(100),nullable=False)
    fname = db.Column(db.String(100),nullable=False)
    lname = db.Column(db.String(50),nullable=False)
    country = db.Column(db.String(50),nullable=False)
    age = db.Column(db.Integer)
    total_mails = db.Column(db.Integer,default=0)

    def __repr__(self):
        return f'user {self.email_id}'

class Inbox(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.String(100),nullable=False)
    to_id = db.Column(db.String(100),nullable=False)
    times = db.Column(db.DateTime,default=datetime.utcnow)
    subj = db.Column(db.String(50),nullable=False)
    content = db.Column(db.String(50),nullable=False)
    
    def __repr__(self):
        return f'inbox {self.aid}'

class Trash(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.String(100),nullable=False)
    to_id = db.Column(db.String(100),nullable=False)
    times = db.Column(db.DateTime,default=datetime.utcnow)
    subj = db.Column(db.String(50),nullable=False)
    content = db.Column(db.String(50),nullable=False)
    
    def __repr__(self):
        return f'trash {self.aid}'

class Allmails(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.String(100),nullable=False)
    to_id = db.Column(db.String(100),nullable=False)
    times = db.Column(db.DateTime,default=datetime.utcnow)
    subj = db.Column(db.String(50),nullable=False)
    content = db.Column(db.String(50),nullable=False)
    
    def __repr__(self):
        return f'allmail {self.aid}'

class Sent(db.Model):
    aid = db.Column(db.Integer, primary_key=True)
    from_id = db.Column(db.String(100),nullable=False)
    to_id = db.Column(db.String(100),nullable=False)
    times = db.Column(db.DateTime,default=datetime.utcnow)
    subj = db.Column(db.String(50),nullable=False)
    content = db.Column(db.String(50),nullable=False)
    
    def __repr__(self):
        return f'Sent {self.aid}'





@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/register',methods=['GET','POST'])
def registerme():
    if (request.method=='POST'):
        fn = request.form['firstname']
        ln = request.form['lastname']
        eml = request.form['email']
        pas = request.form['pass']
        cont = request.form['country']
        ag = request.form['age']
        if any([fn=='',ln=='',eml=='',pas=='',cont=='',str(ag)=='']):
            return "any Field cannot be left empty"
        else:
            alreadyuser = Userinfo.query.filter_by(email_id=eml).all()
            if (len(alreadyuser) == 0):
                newuser = Userinfo(fname=fn,lname=ln,country=cont,age=ag,password=pas,email_id=eml)
                db.session.add(newuser)
                db.session.commit();
                return redirect('/')
            else:
                return "email should be unique"
    else:
        return render_template('register.html')


@app.route('/login',methods=['GET','POST'])
def login():
    if (request.method == 'POST'):
        eml = request.form['email']
        pas = request.form['pass']
        if(any([eml=='',pas==''])):
            return "Fields cannot be remain empty"
        else:
            user = Userinfo.query.filter_by(email_id=eml,password=pas).all()
            if(len(user) == 0):
                return "wrong email or password"
            else:
                return redirect(f'/login/{user[0].aid}/{user[0].email_id}/inbox')
    else:
        return render_template('login.html')    


@app.route('/login/<int:aid>/<string:emale>/inbox')
def afterlogin(aid,emale):
    inboxes = Inbox.query.filter_by(to_id = emale).all()
    return render_template('afterlogin.html',inbox_mails=inboxes,userid=aid,useremail=emale,listlen=len(inboxes),mailtype=0)


@app.route('/login/<int:aid>/<string:emale>/compose',methods=['GET','POST'])
def composemail(aid,emale):
    if (request.method=='POST'):
        eml = request.form['remail'].strip()
        subj = request.form['subject'].strip()
        content = request.form['content__area'].strip()
        if any([eml=='',subj=='',content=='']):
            return "fields cannot be leave blank"
        else:
            isvalid = len(Userinfo.query.filter_by(email_id=eml).all()) >0
            if isvalid:
                curtime = datetime.now()
                newsent = Sent(from_id=emale,to_id=eml,times=curtime,subj=subj,content=content)
                newinbox = Inbox(from_id=emale,to_id=eml,times=curtime,subj=subj,content=content)
                db.session.add(newsent)
                db.session.commit()
                db.session.add(newinbox)
                db.session.commit()
                user = Userinfo.query.filter_by(email_id=eml).all()
                user[0].total_mails = user[0].total_mails+1
                db.session.commit()
                return redirect(f'/login/{aid}/{emale}/inbox')
            else:
                return f'email not correct'
    else:
        return render_template('compose.html',aidi = aid,useremail=emale)    

@app.route('/login/<int:aid>/<string:emale>/trash')
def trashmail(aid,emale):
    inboxes = Trash.query.filter_by(to_id = emale).all()
    return render_template('afterlogin.html',inbox_mails=inboxes,userid=aid,useremail=emale,listlen=len(inboxes),mailtype=1)

@app.route('/login/<int:aid>/<string:emale>/sent')
def sendmail(aid,emale):
    inboxes = Sent.query.filter_by(from_id = emale).all()
    return render_template('afterlogin.html',inbox_mails=inboxes,userid=aid,useremail=emale,listlen=len(inboxes),mailtype=2)

@app.route('/login/<int:aid>/<string:emale>/delete/<int:mail_no>')
def delete_mail(aid,emale,mail_no):
    curmail = Inbox.query.get_or_404(mail_no)
    newTrash = Trash(from_id=curmail.from_id,to_id=curmail.to_id,times=curmail.times,subj=curmail.subj,content=curmail.content)
    db.session.delete(curmail)
    db.session.commit();
    db.session.add(newTrash)
    db.session.commit();
    user = Userinfo.query.filter_by(email_id=emale).all()
    user[0].total_mails = user[0].total_mails - 1
    db.session.commit()
    return redirect(f'/login/{aid}/{emale}/inbox')

@app.route('/login/<int:aid>/<string:emale>/inbox/read/<int:mail_no>')
def read_mail_inbox(aid,emale,mail_no):
    usermail = Inbox.query.get_or_404(mail_no)
    return render_template('readmail.html',mailinfo=usermail)

@app.route('/login/<int:aid>/<string:emale>/trash/read/<int:mail_no>')
def read_mail_trash(aid,emale,mail_no):
    usermail = Trash.query.get_or_404(mail_no)
    return render_template('readmail.html',mailinfo=usermail)

@app.route('/login/<int:aid>/<string:emale>/sent/read/<int:mail_no>')
def read_mail_sent(aid,emale,mail_no):
    usermail = Sent.query.get_or_404(mail_no)
    return render_template('readmail.html',mailinfo=usermail)



if __name__ == "__main__":
    app.run(debug=True)



# <a href='/login/{{userid}}/{{useremail}}/read/{{mails.aid}}'><button class='btn btn-primary'>Read</button></a>