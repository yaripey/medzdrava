from app import db, login

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

default_avatar_path = ""

class User(UserMixin, db.Model):
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    
    # Role-based system.
    # 1 - patient
    # 2 - vrach
    # 3 - admin
    role = db.Column(db.Integer)
     
    first_name = db.Column(db.String(30), index=True)
    second_name = db.Column(db.String(40), index=True)
    middle_name = db.Column(db.String(40), index=True)
    email = db.Column(db.String(120), index=True)
    sex = db.Column(db.String(10), index=True)
    birthdate = db.Column(db.Date, index=True)
    address = db.Column(db.String(300))
    avatar_file_path = db.Column(db.String(300), default=default_avatar_path)
    phonenumber = db.Column(db.Integer)
    password_hash = db.Column(db.String(128))    

    # Methods
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_phonenumber(self, phonenumber):
        if self.phonenumber == phonenumber:
            return True
        else:
            return False

    def get_id(self):
        return str(self.id).zfill(6)

    # Representation
    def __repr__(self):
        return '<User {}>'.format(self.id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('user.id'))
    id_vrach = db.Column(db.Integer, db.ForeignKey('user.id'))
    datetime = db.Column(db.DateTime, index=True)
    zacklucheniye = db.Column(db.String(1000))
    event_name = db.Column(db.String(100))

    def get_vrach(self):
        return User.query.get(self.id_vrach)

    def get_patient(self):
        return User.query.get(self.id_patient)

class Diagnoz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('user.id'))
    diagnoz = db.Column(db.String(500))

class Allergen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_patient = db.Column(db.Integer, db.ForeignKey('user.id'))
    allergen = db.Column(db.String(200))

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String)
    title = db.Column(db.String)
    main_image_path = db.Column(db.String(300))
    is_in_slider = db.Column(db.Boolean)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)
