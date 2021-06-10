from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import os

db = SQLAlchemy()

class Person(db.Model):
  __tablename__ = "person"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  last_name = db.Column(db.String(120), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  salt = db.Column(db.String(100), nullable=False)
  hased_password = db.Column(db.String(240), unique=False, nullable=False)
  dates_as_profesional = db.relationship('Appointment', foreign_keys='Appointment.profesional_id', backref="profesional")
  dates_as_user = db.relationship('Appointment', foreign_keys='Appointment.user_id', backref="user")
  report_as_profesional = db.relationship('Report', foreign_keys='Report.profesional_id', backref="profesional")
  report_as_user = db.relationship('Report', foreign_keys='Report.user_id', backref="user")
  #THIS COLUMN WILL BE USED FOR DECIDE USER TYPES
  type = db.Column(db.String(50), nullable=False)

  __mapper_args__ = {
    "polymorphic_identity": 'person',
    'polymorphic_on': type
  }

  def serialize(self):
    return {
      "id": self.id,
      "email": self.email,
      # do not serialize the password, its a security breach
    }


#USER

class User(Person):
  __tablename__ = None
  __mapper_args__ = {
        'polymorphic_identity':'user'
  }

  def __init__(self, **kwargs):
    print(kwargs)
    self.name = kwargs.get('name')
    self.last_name = kwargs.get('last_name')
    self.email = kwargs.get('email')
    self.salt = os.urandom(16).hex()
    self.set_password(kwargs.get('password'))

  @classmethod
  def create(cls, **kwargs):
    user = cls(**kwargs)
    db.session.add(user)

    try:
      db.session.commit()
    except Exception as error:
      print(error.args)
      db.session.rollback()
      return False

    return user


  def set_password(self, password):
    self.hased_password = generate_password_hash(
      f"{password}{self.salt}"
    )

  def check_password(self, password):
    return check_password_hash(self.hased_password, f"{password}{self.salt}")

  def serialize(self):
    return {
      "id": self.id,
      "name": self.name,
      "last_name": self.last_name,
      "email": self.email,
      "type": self.type,
      # do not serialize the password, its a security breach
    }


class Profesional(Person):
  __tablename__ = None
  is_verified = db.Column(db.Boolean, unique=False, default=False)
  id_image = db.Column(db.String(240))
  title_image = db.Column(db.String(240))


  __mapper_args__ = {
        'polymorphic_identity':'profesional'
    }


class Report(db.Model):
  __tablename__ = 'report'
  id = db.Column(db.Integer, primary_key=True)
  diagnostic = db.Column(db.String(240))
  progress = db.Column(db.String(240))
  finished = db.Column(db.String(240))
  bitacora = db.Column(db.String(240))
  user_id = db.Column(db.Integer, db.ForeignKey('person.id'))
  profesional_id = db.Column(db.Integer, db.ForeignKey('person.id'))



class Appointment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  created_date = db.Column(db.DateTime(timezone=True), default=db.func.now())
  day_date = db.Column(db.String(50), nullable=False)
  start_date = db.Column(db.String(50), nullable=False)
  end_date = db.Column(db.String(50), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('person.id'))
  profesional_id = db.Column(db.Integer, db.ForeignKey('person.id'))



