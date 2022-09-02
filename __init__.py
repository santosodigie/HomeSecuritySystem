from abc import ABC

from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_mysqldb import MySQL, MySQLdb
from mysql.connector import connect, Error
# from pubnub.callbacks import SubscribeCallback
import MySQLdb.cursors
import re
from collections import OrderedDict
from pubnub.callbacks import SubscribeCallback
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

app = Flask(__name__)
app.secret_key = "AzurCam123"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "azurcam"

db = MySQL(app)
print(db)

pnconfig = PNConfiguration()
pnconfig.subscribe_key = "sub-c-60d39bd0-5cfb-11ec-96e9-32997ff5e1b9"
pnconfig.publish_key = "pub-c-0586af82-d21f-4eb0-a261-9b0ec1e03ba0"

pubnub = PubNub(pnconfig)
alive = 0
data = {}


#
@app.route('/', methods=['GET', 'POST'])
def index():
    msg = ''
    if request.method == "POST":
        if 'email' in request.form and 'password' in request.form:
            email = request.form['email']
            password = request.form['password']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)

            cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, password,))
            account = cursor.fetchone()

            if account is not None:
                session['loggedin'] = True
                session['user_id'] = account['user_id']
                session['username'] = account['username']
                session['iot_id'] = account['iot_id']
                return redirect(url_for('home'))
            else:
                msg = 'Incorrect username or password'

    return render_template('index.html', msg=msg)


#
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash("You have been logged out", "info")
    return redirect(url_for('index'))


#
@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        if 'email' in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * FROM users WHERE username = %s or email = %s', (username, email))
            account = cursor.fetchone()

            if account:
                msg = 'Account already exists!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            else:
                cursor.execute('INSERT INTO azurcam.users(username, password, email)VALUES(%s, %s, %s)',
                               (username, password, email,))
                db.connection.commit()
                # msg = 'You have successfully registered!'
                return redirect(url_for('index'))

        elif request.method == 'POST':
            msg = 'Please fill out the form!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template('register.html', msg=msg)


@app.route('/home')
def home():
    if 'loggedin' in session:
        iot_id = session['iot_id']
        cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
        sql = "SELECT * FROM images WHERE image_reference LIKE '%s-%%' " % iot_id
        print(sql)
        cursor.execute(sql)
        info = cursor.fetchall()
        userDict = {}
        for ino in info:
            userDict[ino["image_reference"]] = ino["time"]

        res = OrderedDict(reversed(list(userDict.items())))
        length = len(res)
        print(length)
        return render_template("home.html", userDict=res, length=length, username=session['username'])
    else:
        (print("Not Signed In"))
        return render_template("index.html")


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if 'loggedin' in session:
        if request.method == 'POST':
            if 'iot_id' in request.form:
                username = session['username']
                iot_id = request.form['iot_id']

                cursor = db.connection.cursor(MySQLdb.cursors.DictCursor)
                sql = "UPDATE users SET iot_id = '%s' WHERE username = '%s'" % (iot_id, username)
                cursor.execute(sql)
                db.connection.commit()
                session['iot_id'] = iot_id
            return redirect(url_for('home'))
        else:
            return render_template('setup.html')
    # salt
    else:
        (print("Not Signed In"))
        return render_template("index.html")


"""
RECEIVING DETECTED MOTION FROM PUBNUB
"""


class MySubscribeCallback(SubscribeCallback, ABC):
    def message(self, pubnub, message):
        messageArray = message.__dict__
        image_reference = messageArray['message']['image-reference']
        time = messageArray['message']['time']
        print(time)
        update_query = "INSERT INTO images (image_reference, time) VALUES ('%s', '%s')" % (image_reference, time)
        print(update_query)
        try:
            with connect(
                    host="localhost",
                    user="root",
                    password="",
                    database="azurcam"
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(update_query)
                    connection.commit()
        except Error as e:
            print(e)


pubnub.add_listener(MySubscribeCallback())

pubnub.subscribe().channels("azurcam-channel").with_presence() \
    .execute()

if __name__ == '__main__':
    app.run()
