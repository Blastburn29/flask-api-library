from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config["JWT_SECRET_KEY"] = "13fca337e65642e3b0a290d25238647d"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
jwt = JWTManager(app)
db = SQLAlchemy(app)
# app.config['SECRET_KEY'] = ''