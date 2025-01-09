import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user, login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# --- Konfiguracja aplikacji ---
app = Flask(__name__)
app.secret_key = "sekretny_klucz"  # W praktyce ustaw w bezpiecznym miejscu (np. zmienna środowiskowa)

# --- Konfiguracja bazy SQLite ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'todo.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Konfiguracja Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # nazwa widoku, na który zostanie przekierowany niezalogowany użytkownik

# --- MODELE ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # Pomocnicza metoda ustawiania hasła (tworzy hash zamiast zwykłego tekstu)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Metoda sprawdzająca czy hasło jest poprawne
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    is_done = db.Column(db.Boolean, default=False, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))

# Tworzymy tabele w bazie przy starcie (o ile jeszcze nie istnieją)
with app.app_context():
    db.create_all()

# --- Funkcje Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES / ENDPOINTY ---

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return render_template('home.html')  # np. jakaś prosta strona powitalna

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Sprawdzenie, czy użytkownik już nie istnieje
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Użytkownik o podanej nazwie już istnieje!', 'danger')
            return redirect(url_for('register'))

        # Tworzymy nowego użytkownika
        new_user = User(username=username)
        new_user.set_password(password)  # hashujemy hasło
        db.session.add(new_user)
        db.session.commit()

        flash('Rejestracja przebiegła pomyślnie! Możesz się teraz zalogować.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Logujemy użytkownika
            login_user(user)
            flash('Zalogowano pomyślnie!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Niepoprawny login lub hasło.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Zostałeś wylogowany.', 'info')
    return redirect(url_for('home'))

@app.route('/tasks', methods=['GET', 'POST'])
@login_required  # dostęp tylko dla zalogowanego użytkownika
def index():
    if request.method == 'POST':
        task_title = request.form.get('task_title')
        if task_title:
            new_task = Task(title=task_title, user_id=current_user.id)
            db.session.add(new_task)
            db.session.commit()
            flash('Dodano nowe zadanie!', 'success')
        return redirect(url_for('index'))

    tasks_todo = Task.query.filter_by(user_id=current_user.id, is_done=False).all()
    tasks_done = Task.query.filter_by(user_id=current_user.id, is_done=True).all()
    return render_template('index.html', tasks_todo=tasks_todo, tasks_done=tasks_done)

@app.route('/done/<int:task_id>')
@login_required
def mark_done(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.is_done = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/undo/<int:task_id>')
@login_required
def mark_undo(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.is_done = False
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

# --- URUCHOMIENIE ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

