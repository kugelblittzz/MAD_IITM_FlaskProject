from flask import Flask,render_template
import sqlite3
import os.path
from flask_sqlalchemy import SQLAlchemy
from database import db
import datetime





class Users(db.Model):
    username = db.Column(db.String(100), unique=True,primary_key = True)
    password = db.Column(db.String(100))
    followers=db.Column(db.Integer)
    posts_num=db.Column(db.Integer)

    def __init__(self,username,password,followers,posts_num):
        self.username=username
        self.password=password
        self.followers=followers
        self.posts_num=posts_num


class Posts(db.Model):
    Id=db.Column(db.String(100),unique=True,primary_key=True)
    username = db.Column(db.String(100),db.ForeignKey(Users.username))
    title=db.Column(db.String(500))
    desc=db.Column(db.String(500))
    img_url=db.Column(db.String(500))
    timestamp=db.Column(db.DateTime)

    def __init__(self,Id,username,title,desc,img_url,timestamp):
        self.Id=Id
        self.username=username
        self.title=title
        self.desc=desc
        self.img_url=img_url
        self.timestamp=datetime.datetime.now()

class Follows(db.Model):
    Id=db.Column(db.String(100),unique=True,primary_key=True)
    follower=db.Column(db.String(100),db.ForeignKey(Users.username))
    following=db.Column(db.String(100),db.ForeignKey(Users.username))

    def __init__(self,Id,follower,following):
        self.Id=Id
        self.follower=follower
        self.following=following







