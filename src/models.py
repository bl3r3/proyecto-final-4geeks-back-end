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
  # report_as_profesional = db.relationship('Report', foreign_keys='Report.profesional_id', backref="profesional")
  # report_as_user = db.relationship('Report', foreign_keys='Report.user_id', backref="user")
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

#PROFESSIONAL
class Profesional(Person):
  __tablename__ = None
  is_verified = db.Column(db.Boolean, unique=False, default=False)
  
  __mapper_args__ = {
        'polymorphic_identity':'profesional'
    }

  def __init__(self, **kwargs):
    print(kwargs)
    self.name = kwargs.get('name')
    self.last_name = kwargs.get('last_name')
    self.email = kwargs.get('email')
    self.salt = os.urandom(16).hex()
    self.set_password(kwargs.get('password'))
    self.is_verified = kwargs.get('is_verified')

  @classmethod
  def create_profesional(cls, **kwargs):
    profesional = cls(**kwargs)
    db.session.add(profesional)

    try:
      db.session.commit()
    except Exception as error:
      print(error.args)
      db.session.rollback()
      return False

    return profesional

  def serialize(self):
    return {
      "id": self.id,
      "name": self.name,
      "last_name": self.last_name,
      "email": self.email,
      "type": self.type,
      # do not serialize the password, its a security breach
    }
  def set_password(self, password):
    self.hased_password = generate_password_hash(
      f"{password}{self.salt}"
    )

  def check_password(self, password):
    return check_password_hash(self.hased_password, f"{password}{self.salt}")


#REPORTE DEL PACIENTE
# class Report(db.Model):
#   __tablename__ = 'report'
#   id = db.Column(db.Integer, primary_key=True)
#   diagnostic = db.Column(db.String(240))
#   paciente = db.Column(db.String(240))

#   def __init__(self, **kwargs):
#     print(kwargs)
#     self.diagnostic = kwargs.get('diagnostic')
#     self.paciente = kwargs.get('paciente')

#   @classmethod
#   def create(cls, **kwargs):
#     report = cls(**kwargs)
#     db.session.add(report)

#     try:
#       db.session.commit()
#     except Exception as error:
#       print(error.args)
#       db.session.rollback()
#       return False
#     return report

#   def serialize(self):
#     return {
#       "id": self.id,
#       "diagnostic": self.diagnostic,
#       "exercise_id": self.exercise_id,
#       "user_id": self.user_id,
#       "profesional_id": self.profesional_id,
#       "profesional": self.profesional.serialize()
#     }


#EJERCICIOS DEL REPORTE
# class Exercise(db.Model):
#   __tablename__ = 'exercise'
#   id = db.Column(db.Integer, primary_key=True)
#   description = db.Column(db.String(240), nullable=False)
#   #THIS COLUMN WILL BE USED FOR DECIDE EXERCISE STATUS
#   status = db.Column(db.Boolean, unique=False, default=False)

#   def __init__(self, **kwargs):
#     print(kwargs)
#     self.description = kwargs.get('description')
#     self.status = kwargs.get('status')

#   @classmethod
#   def create(cls, **kwargs):
#     exercise = cls(**kwargs)
#     db.session.add(exercise)

#     try:
#       db.session.commit()
#     except Exception as error:
#       print(error.args)
#       db.session.rollback()
#       return False
#     return exercise

#   def serialize(self):
#     return {
#       "id": self.id,
#       "description": self.description,
#       "status": self.status
#     }


class Appointment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  created_date = db.Column(db.DateTime(timezone=True), default=db.func.now())
  day_date = db.Column(db.String(50), nullable=False)
  schedule = db.Column(db.String(50), nullable=False)
  via = db.Column(db.String(50), nullable=False)
  user_id = db.Column(db.Integer, db.ForeignKey('person.id'))
  profesional_id = db.Column(db.Integer, db.ForeignKey('person.id'))

  def __init__(self, **kwargs):
    print(kwargs)
    self.day_date = kwargs.get('day_date')
    self.schedule = kwargs.get('schedule')
    self.via = kwargs.get('via')
    self.user_id = kwargs.get('user_id')
    self.profesional_id = kwargs.get('profesional_id')

  @classmethod
  def create(cls, **kwargs):
    appointment = cls(**kwargs)
    db.session.add(appointment)

    try:
      db.session.commit()
    except Exception as error:
      print(error.args)
      db.session.rollback()
      return False
    return appointment

  def serialize(self):
    return {
      "id": self.id,
      "day_date": self.day_date,
      "schedule": self.schedule,
      "via": self.via,
      "user_id": self.user_id,
      "profesional_id": self.profesional_id,
      "profesional": self.profesional.serialize()
    }





