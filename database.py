from flask import Flask,render_template
import sqlite3
import os.path
from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()
