from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 데이터베이스 설정

db = SQLAlchemy()

# 사용자 모델
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'claude'}  # claude 스키마 지정
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    conversations = db.relationship('Conversation', backref='user', lazy=True)

# 대화 히스토리 모델
class Conversation(db.Model):
    __tablename__ = 'conversations'
    __table_args__ = {'schema': 'claude'}  # claude 스키마 지정
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('claude.users.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
