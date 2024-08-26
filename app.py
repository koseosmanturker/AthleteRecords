from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ilbank_athletes.db'
db = SQLAlchemy(app)

class Athlete(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    division = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    successes = db.relationship('Success', backref='athlete', lazy=True)

class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    successes = db.relationship('Success', backref='tournament', lazy=True)

class Success(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athlete.id'), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    result = db.Column(db.String(100), nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

@app.before_first_request
def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/information_page')
def information_page():
    return render_template('information_page.html')

@app.route('/athletes_info')
def athletes_info():
    athletes = Athlete.query.all()
    return render_template('athletes_info.html', athletes=athletes)

@app.route('/athlete/<int:athlete_id>')
def athlete_achievements(athlete_id):
    athlete = Athlete.query.get_or_404(athlete_id)
    successes = Success.query.filter_by(athlete_id=athlete_id).join(Tournament).all()
    return render_template('athlete_detail.html', athlete=athlete, successes=successes)

@app.route('/tournaments_info')
def tournaments_info():
    tournaments = Tournament.query.all()
    return render_template('tournaments_info.html', tournaments=tournaments)

@app.route('/tournament/<int:tournament_id>')
def tournament_participants(tournament_id):
    tournament = Tournament.query.get_or_404(tournament_id)
    successes = Success.query.filter_by(tournament_id=tournament_id).all()
    athletes = [Athlete.query.get(s.athlete_id) for s in successes]
    participants_with_successes = list(zip(athletes, successes))
    return render_template('tournament_detail.html', tournament=tournament, participants_with_successes=participants_with_successes)

@app.route('/add_athlete', methods=['GET', 'POST'])
def add_athlete():
    if request.method == 'POST':
        name = request.form['athlete_name']
        surname = request.form['athlete_surname']
        division = request.form['athlete_division']
        category = request.form['athlete_category']
        athlete = Athlete(name=name, surname=surname, division=division, category=category)
        db.session.add(athlete)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_athlete.html')

@app.route('/add_tournament', methods=['GET', 'POST'])
def add_tournament():
    if request.method == 'POST':
        name = request.form['tournament_name']
        date = request.form['tournament_date']
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        tournament = Tournament(name=name, date=date_obj)
        db.session.add(tournament)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_tournament.html')

@app.route('/add_success', methods=['GET', 'POST'])
def add_success():
    if request.method == 'POST':
        athlete_id = request.form['athlete_id']
        tournament_id = request.form['tournament_id']
        result = request.form['result']
        success = Success(athlete_id=athlete_id, tournament_id=tournament_id, result=result)
        db.session.add(success)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    athletes = Athlete.query.all()
    tournaments = Tournament.query.all()
    return render_template('add_success.html', athletes=athletes, tournaments=tournaments)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        return 'Invalid credentials'
    return render_template('admin_login.html')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html')

##@app.before_first_request
##def create_admin():
##    with app.app_context():
##        if not Admin.query.first():
##            default_username = 'admin'
##            default_password = 'admin'
##            hashed_password = generate_password_hash(default_password)
##            new_admin = Admin(username=default_username, password=hashed_password)
##            db.session.add(new_admin)
##            db.session.commit()
##            print(f'Admin user created with username: {default_username} and password: {default_password}')
##        else:
##            print('Admin user already exists.')


@app.route('/landing')
def landing_page():
    return render_template('landing_page.html')

@app.route('/')
def index():
    return redirect(url_for('landing_page'))

if __name__ == '__main__':
    app.run(debug=True)
