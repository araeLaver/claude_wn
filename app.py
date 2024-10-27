from flask import Flask, request, render_template, redirect, jsonify, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from database import db, User, Conversation, Message
from claude_api import call_claude_api
import os

from dotenv import load_dotenv
from flask_migrate import Migrate
from sqlalchemy import text
import logging

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

load_dotenv()
app = Flask(__name__)

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

db.init_app(app)
migrate = Migrate(app, db)

print(os.environ.get('DATABASE_URI'))

# 사용자 인증 (간단한 세션 사용)
app.secret_key = os.environ.get('SECRET_KEY')

# 홈 페이지
@app.route('/')
def index():
    user = db.session.get(User, 1)  # 데모를 위해 사용자 ID 1 사용
    if not user:
        user = User(username='Test User', email='test@example.com')
        db.session.add(user)
        db.session.commit()

    conversations = Conversation.query.filter_by(user_id=user.id).order_by(Conversation.created_at.desc()).all()
    return render_template('main.html', conversations=conversations)

# 대화 생성 및 메시지 처리
@app.route('/generate', methods=['POST'])
def generate():
    user = db.session.get(User, 1)  # 데모를 위해 사용자 ID 1 사용

    prompt = request.form['prompt']
    conversation_id = request.form.get('conversation_id')

    if conversation_id:
        try:
            conversation_id = int(conversation_id)
            conversation = Conversation.query.get(conversation_id)
            if not conversation:
                # 존재하지 않는 conversation_id인 경우 새로운 Conversation 생성
                conversation = Conversation(user_id=user.id)
                db.session.add(conversation)
                db.session.commit()  # 커밋하여 데이터베이스에 저장
        except ValueError:
            # conversation_id가 유효한 정수가 아닌 경우 처리
            conversation = Conversation(user_id=user.id)
            db.session.add(conversation)
            db.session.commit()  # 커밋하여 데이터베이스에 저장
    else:
        conversation = Conversation(user_id=user.id)
        db.session.add(conversation)
        db.session.commit()  # 커밋하여 데이터베이스에 저장

    # 사용자 메시지 저장
    user_message = Message(conversation_id=conversation.id, role='user', content=prompt)
    db.session.add(user_message)
    db.session.commit()  # 메시지 저장을 위한 커밋

    # 대화의 모든 메시지를 가져와 챗봇에게 전달
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at).all()
    message_list = [{'role': msg.role, 'content': msg.content} for msg in messages]

    # 챗봇 응답 생성
    response_text = call_claude_api(message_list)

    # 챗봇 응답 메시지 저장
    assistant_message = Message(conversation_id=conversation.id, role='assistant', content=response_text)
    db.session.add(assistant_message)
    db.session.commit()  # 응답 메시지 저장을 위한 커밋

    return redirect(url_for('detail', conversation_id=conversation.id))
    #  return jsonify({'conversation_id': conversation.id, 'response': response_text})




# 대화 상세 페이지
@app.route('/detail/<int:conversation_id>')
def detail(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    messages = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at).all()
    return render_template('detail.html', conversation=conversation, messages=messages)

# 대화 삭제
@app.route('/delete/<int:conversation_id>', methods=['POST'])
def delete_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    messages = Message.query.filter_by(conversation_id=conversation.id).all()

    for message in messages:
        db.session.delete(message)
    db.session.delete(conversation)
    db.session.commit()
    return jsonify({"message": "Conversation deleted"})

# 데이터베이스 연결 테스트
@app.route('/test_db_connection')
def test_db_connection():
    try:
        # 데이터베이스에 간단한 쿼리 실행
        result = db.session.execute(text('SELECT 1'))
        # 결과 확인
        for row in result:
            print(row)
        return '데이터베이스 연결 성공!'
    except Exception as e:
        print(f'데이터베이스 연결 실패: {e}')
        return f'데이터베이스 연결 실패: {e}'

# 테스트 데이터베이스 삽입
@app.route('/test_db')
def test_db():
    try:
        # 데이터베이스에 간단한 데이터 삽입
        test_user = User(username='TestUser', email='testuser@example.com')
        db.session.add(test_user)
        db.session.commit()
        return '데이터베이스에 데이터 저장 성공!'
    except Exception as e:
        return f'데이터베이스에 데이터 저장 실패: {e}'

if __name__ == '__main__':
    app.run(debug=True)
