# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///testDB.db '
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class IPFS_hash(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  type = db.Column(db.String())
  name = db.Column(db.String(120))
  hash = db.Column(db.String(120), unique=True)
  def __init__(self, type, name, hash):
    self.type = type
    self.name = name
    self.hash = hash
  def __repr__(self):
    return '<File %r>' % self.name

