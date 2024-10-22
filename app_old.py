from flask import Flask, request, render_template, redirect, jsonify
from datetime import datetime
from database import db, User, Conversation
from claude_api import call_claude_api

app = Flask(__name__)

# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://koyeb-adm:TRQuyavq9W5B@ep-blue-unit-a2ev3s9x.eu-central-1.pg.koyeb.app:5432/koyebdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# 기본 경로 추가 (홈페이지 또는 인덱스 페이지)
@app.route('/')
def index():
    texts = Conversation.query.all()
    return render_template('main.html', texts=texts, card_view=True)

# 글 생성 API (사용자가 프롬프트를 입력하고 AI 응답 받음)
@app.route('/generate', methods=['POST'])
def generate():
    # 사용자 확인 및 생성
    print("사용자 확인 및 생성 시작")
    user = User.query.get(1)
    if not user:
        user = User(id=1, username="Test User", email="testuser@example.com", created_at=datetime.now())
        db.session.add(user)
        db.session.commit()
    print("사용자 확인 및 생성 완료")

    # API 호출
    prompt = request.form['prompt']
    print("Claude API 호출 시작, 프롬프트:", prompt)
    response_text = call_claude_api(prompt)
    
    # 오류가 있을 경우 사용자에게 명확한 메시지를 반환
    if "Error:" in response_text:
        print("API 호출 오류:", response_text)
        return render_template('main.html', texts=Conversation.query.all(), error_message="API 호출 오류가 발생했습니다. 관리자에게 문의하세요.", response_text=None, card_view=True)

    print("Claude API 호출 완료, 응답:", response_text)

    # 생성된 텍스트 데이터베이스에 저장
    new_text = Conversation(prompt=prompt, response=response_text, created_at=datetime.now(), user_id=user.id)
    db.session.add(new_text)
    db.session.commit()
    print("생성된 텍스트 데이터베이스에 저장 완료")

    return redirect(f'/detail/{new_text.id}')

# 사용자 생성 API (테스트용)
@app.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'], created_at=datetime.now())
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created", "user_id": new_user.id})

# 대화 상세 페이지
@app.route('/detail/<int:id>', methods=['GET'])
def detail(id):
    conversation = Conversation.query.get_or_404(id)
    return render_template('detail.html', conversation=conversation, texts=Conversation.query.all())

# 대화 삭제 API
@app.route('/delete/<int:id>', methods=['POST'])
def delete_conversation(id):
    conversation = Conversation.query.get_or_404(id)
    db.session.delete(conversation)
    db.session.commit()
    return jsonify({"message": "Conversation deleted"})

if __name__ == '__main__':
    app.run(debug=True)
