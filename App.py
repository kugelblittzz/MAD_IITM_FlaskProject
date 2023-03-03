from flask import *
import sqlite3
import os.path
from flask_sqlalchemy import SQLAlchemy
from Models import Users,Posts,Follows
from database import db
import uuid
import datetime



app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(BASE_DIR, 'App.db')
db_path = os.path.join(BASE_DIR, "App.db")

app.secret_key = "ilham"  


db.init_app(app)




#Entry point of the application
@app.route('/')
def index():
    session.pop('username',None)
    return render_template("index.html")

#route to serve signup page
@app.route("/signup")
def Signup():
    if 'username' in session:
        return redirect(url_for('Dashboard'))
    else:
        return render_template("Signup.html")

#route to serve signup page
@app.route('/signin')
def Signin():
    if 'username' in session:
        return redirect(url_for('Dashboard'))
    else:
        return render_template("Signin.html")
    


#Handles Registering of User
@app.route('/signup/register',methods=['GET',"POST"])
def Register():
    username=request.form['username']
    password=request.form['password']
    q=Users.query.filter(Users.username==username).all()
    if(q):
        return render_template("Signup.html",data="Username Already Exists!!")
    else:
        user=Users(username,password,0,0)
        db.session.add(user)
        db.session.commit()
        print("null")
        return render_template("Signin.html")

#Handles Signin of User
@app.route('/signin/register',methods=['GET',"POST"])
def Login():
    username=request.form['username']
    password=request.form['password']
    q=Users.query.filter(Users.username==username).all()
    if(q):
        if(q[0].password==password):
            session['username']=username
            return redirect(url_for('Dashboard')) 
        else:
            return render_template("Signin.html",data="Incorrect Password!")
        # return render_template("Dashboard.html",username=username,followers=q[0].followers,postno=q[0].posts_num)
    else:
        return render_template("Signin.html",data="Username not found!")

#Serves Dashboard only after login of user
@app.route('/dashboard')
def Dashboard():
    if 'username' in session:
        username=session['username']
        q=Users.query.filter(Users.username==username).all()
        q1=Posts.query.filter(Posts.username==username).order_by(Posts.timestamp).all()
        q1.reverse()


        return render_template("Dashboard.html",username=username,followers=q[0].followers,postno=q[0].posts_num,posts=q1)
    else:
        return render_template("Signin.html",data="Please Login to see Dashboard!")

#Handles logging out of the user
@app.route('/logout')
def Logout():
    session.pop('username',None)
    return redirect(url_for('index'))

#Handles new post of user
@app.route('/dashboard/post',methods=['GET',"POST"])
def AddPost():
    if 'username' in session:
        try:
            username=session['username']
            Id=str(uuid.uuid4())
            print(Id)
            title=request.form['title']
            desc=request.form['desc']
            url=request.form['url']
            timestamp=datetime.datetime.now()
            post=Posts(Id,username,title,desc,url,timestamp)
            db.session.add(post)
            db.session.commit()
            user = Users.query.filter_by(username=username).first()
            print(user)
            user.posts_num +=1
            db.session.commit()
            return redirect(url_for('Dashboard'))
        except Exception as e:
            print(e)
            return "Erorr occured"
    else:
        return render_template("Signin.html",data="Please Login to see Dashboard or post!")

#Handles Deletion of a post
@app.route('/dashboard/delete/<Id>')
def delPost(Id):
    print(Id)
    if 'username' in session:
        username=session['username']
        post=Posts.query.get(Id)
        db.session.delete(post)
        db.session.commit()
        user = Users.query.filter_by(username=username).first()
        print(user)
        user.posts_num -=1
        db.session.commit()
        return Dashboard()
    else:
         return render_template("Signin.html",data="Please Login to see Dashboard or delete a post!")


#To get list of all users
@app.route('/users')
def GetUserss():
    if 'username' in session:
        return render_template('Users.html')

#Handles searching of user
@app.route('/users/search',methods=['GET',"POST"])
def UserSearch():
    if 'username' in session:
        try:
            username=request.form['username']
        except:
            username=""
        q=Users.query.filter(Users.username.contains(username)).all()
        data=[]
        for user in q:
            q1=Follows.query.filter(Follows.follower==session['username'],Follows.following==user.username).all()
            print(q1)
            if(q1):
                user.follow="Following"
            else:
                user.follow="Follow"
            print(user.follow)
            if(user.username!=session['username']):
                data.append(user)

        return render_template('Users.html',users=data,message="Search Results : ")
    else:
        render_template("Signin.html",data="Please Login First")

#Handles follow operation
@app.route('/users/search/follow',methods=['GET',"POST"])
def Follow():
    if 'username' in session:
        q=Follows.query.filter(Follows.follower==session['username'],Follows.following==request.form['username']).all()
        print(q)
        if(q):
            for i in q:
                db.session.delete(i)
                db.session.commit()
                userq = Users.query.filter_by(username=i.following).first()
                userq.followers -=1
                db.session.commit()
            return {'message':'UnFollowed','user':request.form['username']}
        

        else:
            print(request.form)
            Id=str(uuid.uuid4())
            follower=session['username']
            following=request.form['username']
            follow=Follows(Id,follower,following)
            db.session.add(follow)
            db.session.commit()
            userq = Users.query.filter_by(username=following).first()
            userq.followers +=1
            db.session.commit()
            return {'message':'Followed','user':following}
    else:
        render_template("Signin.html",data="Please Login First")
    
#get the feed for user
@app.route('/feed')
def Feed():
    if 'username' in session:
        data=[]
        q1=Follows.query.filter(Follows.follower==session['username']).all()
        for user in q1:
            q2=Posts.query.filter(Posts.username==user.following).order_by(Posts.timestamp).all()
            data=data+q2
        data.sort(key=lambda x:x.timestamp,reverse=True)
        print(data)
        return render_template('Feed.html',posts=data)
        # username=req
        # uest.args['username']
        # print("username is ",username)
        # return render_template('Users.html',users=q,message="Search Results : ")
    else:
        render_template("Signin.html",data="Please Login First")

#Handles editing of a post
@app.route('/dashboard/edit',methods=['GET',"POST","PUT"])
def editpost():
    if 'username' in session:
        Id=request.form['Idedit']
        title=request.form['titleedit']
        desc=request.form['descedit']
        url=request.form['urledit']
        q1=Posts.query.filter(Posts.Id==Id).first()
        q1.title=title
        q1.desc=desc
        q1.img_url=url
        db.session.add(q1)
        db.session.commit()
        print(Id,title,desc,url)
        return Dashboard();
    else:
        render_template("Signin.html",data="Please Login First")

#Fetches the posts of a particular user
@app.route('/users/profile/<user>')
def Userfeed(user):
    users=user
    print("here in the")
    if 'username' in session:
        username=session['username']
        q=Users.query.filter(Users.username==users).first()
        q1=Posts.query.filter(Posts.username==users).order_by(Posts.timestamp).all()
        q1.reverse()


        return render_template("UserProfile.html",username=users,followers=q.followers,postno=q.posts_num,posts=q1)
    else:
        return render_template("Signin.html",data="Please Login to see Dashboard!")











    

if __name__ == "__main__":
    app.run(debug=True)