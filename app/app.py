from flask import Flask, render_template,url_for,redirect,request
from flask_socketio import SocketIO,emit,join_room
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from model import User 



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
#app.config['SECRET_KEY'] = 'secretkey'
login_manager = LoginManager()
login_manager.init_app(app)

current_song = None
current_author = None

USER_ROLES = ('PLAYER','ADMIN')

users = {}

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    print(f"User joined room: {room}")  # Debug statement
    emit('status', {'msg': 'User has joined the room.'}, room=room)
    if current_song and current_author:
        emit('start_live_session', {'song': current_song, 'author': current_author}, room=request.sid)

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/')
def home():
    return render_template('home.html')

@ app.route('/signUp', methods=['GET', 'POST'])
def signUp():
    role = request.args.get('role', 'player')
    if request.method == 'POST':
       # print("POST request received")
        username = request.form['username']
        password = request.form['password']
        instrument = request.form['instrument']
        #print(f"Username: {username}, Password: {password}, Instrument: {instrument}")
        user_id = str(len(users) + 1)
        newUser = User(user_id, username, password, instrument,role)
        #print(newUser)
        users[user_id] = newUser
        #print("Users Dictionary after adding new user:", users)

        return redirect(url_for('login'))

    return render_template('signUp.html',role = role)

# need to change according to users role: admin or player (in the redirect)
@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        for user in users.values():
            if user.username == username and user.password == password:
                login_user(user)
                # check if the user is admin or player and according to that it will send to the appopriate page
                if user.role == 'player':
                    return redirect(url_for('mainPagePlayer'))
                elif user.role == 'admin':
                    return redirect(url_for('mainPageAdmin'))
                else:
                    return "not valid user role"
   
   return render_template('login.html')

@app.route('/searchSong',methods = ["GET","POST"])
@login_required
def searchSong():
    songName = request.form['query']
    return redirect(url_for('resultPage',song = songName))

@app.route('/livePageAdmin',methods = ["GET"])
@login_required
def livePageAdmin():
    song = request.args.get('song')
    author = request.args.get('author')
    return render_template('livePageAdmin.html',song = song,author = author)

@app.route('/livePage',methods = ["GET","POST"])
@login_required
def livePage():
    return render_template('livePage.html')
    
    
# Handle the song selection by the admin
@app.route('/selectSong', methods=['POST'])
def selectSong():
    
    global current_song, current_author
     
    song = request.form['song']
    author = ""
    if song.lower() == "hey jude":
        author = "The Beatles"
    elif song.lower() == "veech shelo":
        author = "Ariel Zilber"
        
        
    current_song = song
    current_author = author

    print(f"Emitting start_live_session event for song: {song} author: {author}")
    
    # Emit an event to all clients in the 'rehearsal_room'
    socketio.emit('start_live_session', {'song': song, 'author': author}, room='rehearsal_room')

    return redirect(url_for('livePageAdmin',song = song,author = author))
    
    
@app.route('/resultPage/<song>')
def resultPage(song):
    author = ""
    if song.lower() == "hey jude":
        author = "The Beatles"
    elif song.lower() == "veech shelo":
        author = "Ariel Zilber"
    else :
        song =""
        author = ""
    return render_template('resultPage.html', song=song, author=author)

@socketio.on('end_session')
def handle_end_session():
    print("Session ended by admin. Notifying all players.")
    # Emit an event to all players in the room to return to the main page
    socketio.emit('session_ended', room='rehearsal_room')

    # Reset current song and author
    global current_song, current_author
    current_song = None
    current_author = None
    print("session_ended event emitted to all players in rehearsal_room.")
    
        
@app.route('/mainPagePlayer', methods = ["GET"])
def mainPagePlayer():
    return render_template('mainPagePlayer.html')

@app.route('/mainPageAdmin', methods= ["GET"])
def mainPageAdmin():
    return render_template('mainPageAdmin.html')




if __name__ == '__main__':
    socketio.run(app, debug=True)
    
    
