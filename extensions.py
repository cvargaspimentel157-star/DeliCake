# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_mysqldb import MySQL

mysql = MySQL()
db = SQLAlchemy()
mail = Mail()
