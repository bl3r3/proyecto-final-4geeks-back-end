from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Person(db.Model):
  __tablename__ = "person"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
  last_name = db.Column(db.String(120), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
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

  def __repr__(self):
    return '<User %r>' % self.username

  def serialize(self):
    return {
      "id": self.id,
      "email": self.email,
      # do not serialize the password, its a security breach
    }

class User(Person):
  __tablename__ = None

  __mapper_args__ = {
        'polymorphic_identity':'user'
    }


class Profesional(Person):
  __tablename__ = None
  is_profesional = db.Column(db.Boolean, unique=False, default=True)
  is_verified = db.Column(db.Boolean, unique=False, default=False)

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



