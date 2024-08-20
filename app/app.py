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
login_manager = LoginManager()
login_manager.init_app(app)

USER_ROLES = ('PLAYER','ADMIN')

users = {}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/')
def home():
    return render_template('home.html')

@ app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    if request.method == 'POST':
       # print("POST request received")
        username = request.form['username']
        password = request.form['password']
        instrument = request.form['instrument']
        #print(f"Username: {username}, Password: {password}, Instrument: {instrument}")
        user_id = str(len(users) + 1)
        newUser = User(user_id, username, password, instrument)
        #print(newUser)
        users[user_id] = newUser
        #print("Users Dictionary after adding new user:", users)

        return redirect(url_for('login'))

    return render_template('signUp.html')

# need to change according to users role: admin or player (in the redirect)
@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        for user in users.values():
            if user.username == username and user.password == password:
                login_user(user)
                return redirect(url_for('mainPagePlayer'))
   
   return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return f'Hello, {current_user.username}!'

@app.route('/mainPagePlayer')
def mainPagePlayer():
    return render_template('mainPagePlayer.html')

@app.route('/livePage')
def livePage():
    return render_template('livePage.html')

if __name__ == '__main__':
    socketio.run(app, debug=True)
    
    
