from flask import Flask, render_template,url_for,redirect,request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from model import User 



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'


users = {}

@app.route('/')
def home():
    return render_template('home.html')

@ app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        instrument = request.form['instrument']
        user_id = str(len(users) + 1)
        users[user_id] = User(user_id, username, password, instrument)
        return redirect(url_for('login'))

    return render_template('signUp.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        for user in users.values():
            if user.username == username and user.password == password:
                login_user(user)
                return redirect(url_for('mainPage.html'))
   return render_template('login.html')
if __name__ == '__main__':
    socketio.run(app, debug=True)
    
    
@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}!'
