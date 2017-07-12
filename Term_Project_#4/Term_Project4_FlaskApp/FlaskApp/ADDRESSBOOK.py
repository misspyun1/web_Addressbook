from flask import Flask, render_template, redirect,request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#데이터 베이스 생성
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///addressbook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = "oodp"

db=SQLAlchemy(app)

#데이터 베이스 테이블 생성
class PERSON(db.Model):
   id=db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
   name=db.Column(db.String(50), nullable=False, default='')
   number=db.Column(db.String(50), nullable=False, default='')
   email=db.Column(db.String(50), nullable=False, default='')
   favorite=db.Column(db.String(10), default="♡")
   deleted=db.Column(db.Boolean, default=False)

   #데이터 베이스 생성자
   def __init__(self, name, number, email):
      self.name=name
      self.number=number
      self.email=email
      self.favorite="♡"
      self.deleted=False

class RECENT(db.Model):
   id=db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
   name=db.Column(db.String(50), nullable=False, default='')
   title=db.Column(db.String(100), nullable=False, default='')
   content=db.Column(db.String(100), nullable=False, default='')
   deleted=db.Column(db.Boolean, default=False)

   #데이터 베이스 생성자
   def __init__(self, name, title, content):
      self.name=name
      self.title=title
      self.content=content
      self.read=False
      self.deleted=False

#메인화면루트
@app.route("/")
def main():
	return render_template('main.html', ADDRESSBOOK=PERSON.query.filter_by(deleted=False).order_by("name").all(), 
		contact_count=PERSON.query.filter_by(deleted=False).count(),trashcount=PERSON.query.filter_by(deleted=True).count())

#추가화면 루트
@app.route("/new", methods=['GET', 'POST'])
def new():
	 if request.method == 'POST':
	 	#빈칸 입력시 추가되지 않음
	 	if not request.form['name'] or not request.form['number'] or not request.form['email']:
	 		flash('Please enter all the fields', 'error')
	 	else:
	 		#입력받은 정보를 받아와서 연락처 추가
	 		NEW=PERSON(request.form['name'],request.form['number'],request.form['email'])
	 		db.session.add(NEW)
	 		db.session.commit()
	 	return redirect("/")

#메세지 보내기 루트
@app.route("/sendmail", methods=['GET', 'POST'])
def send():
	 if request.method == 'POST':
	 	#빈칸 입력시 추가되지 않음
	 	if not request.form['name'] or not request.form['title'] or not request.form['content']:
	 		flash('Please enter all the fields', 'error')
	 	else:
	 		#입력받은 정보를 받아와서 기록에 추가
	 		NEW=RECENT(request.form['name'],request.form['title'],request.form['content'])
	 		db.session.add(NEW)
	 		db.session.commit()
	 	return redirect("/recent")

#즐겨찾기 화면 루트
@app.route("/favorite")
def show_favorite():
	return render_template('favorite.html',contact_count=PERSON.query.filter_by(deleted=False).count(),
		FAVORITE=PERSON.query.filter_by(favorite='♥', deleted=False).order_by("name"),trashcount=PERSON.query.filter_by(deleted=True).count())

#휴지통에서 지우기 루트
@app.route("/abdelete/<id>")
def abdelete(id):
	#데이터 베이스에서 삭제
	abdeleted=PERSON.query.filter_by(id=id)
	abdeleted.delete()
	db.session.commit()
	return redirect("/trash")

#최근기록 지우기 루트
@app.route("/recent/delete/<id>")
def redelete(id):
	#데이터 베이스에서 삭제
	deleted=RECENT.query.filter_by(id=id)
	deleted.delete()
	db.session.commit()
	return redirect("/recent")

#휴지통 루트
@app.route("/trash")
def trash():
	return render_template('trash.html',contact_count=PERSON.query.filter_by(deleted=False).order_by("name").count(),
		trash=PERSON.query.filter_by(deleted=True),trashcount=PERSON.query.filter_by(deleted=True).count())

#복구하기 루트
@app.route("/restore/<id>")
def restore(id):
	#deleted를 false로 바꿔줌
	deleted=PERSON.query.get(id)
	deleted.deleted=False
	db.session.commit()
	return redirect("/")

#삭제하기 루트
@app.route("/delete/<id>")
def delete(id):
	#deleted를 true->false로, flase->true로 바꿔줌
	deleted=PERSON.query.get(id)
	if deleted.deleted==True:
		deleted.deleted=False
	else :
		deleted.deleted=True
	db.session.commit()
	return redirect("/")

#즐겨찾기 추가 루트
@app.route("/favorite/<id>")
def favorite(id):
	#favorite을 true->false로, flase->true로 바꿔줌
	favorite=PERSON.query.get(id)
	if favorite.favorite=="♥":
		favorite.favorite="♡"
	else :
		favorite.favorite="♥"
	db.session.commit()
	return redirect("/")

#검색 루트
@app.route("/search", methods=['POST'])
def search():
	#검색 문자열을 받아와 데이터 베이스에서 찾아 넘겨준다
	string=request.form['string']
	return render_template('search.html', namesearch=PERSON.query.filter_by(name=string, deleted=False).order_by("name").all(),
	numbersearch=PERSON.query.filter_by(number=string, deleted=False).order_by("name").all(),contact_count=PERSON.query.filter_by(deleted=False).count(),
	trashcount=PERSON.query.filter_by(deleted=True).count())

#즐겨찾기 안에서 검색 루트
@app.route("/search/favorite", methods=['POST'])
def search_favorite():
	string=request.form['string']
	return render_template('search.html', namesearch=PERSON.query.filter_by(name=string, favorite='♥', deleted=False).order_by("name").all(),
	numbersearch=PERSON.query.filter_by(number=string, favorite='♥', deleted=False).order_by("name").all(),
	contact_count=PERSON.query.filter_by(deleted=False).count(),trashcount=PERSON.query.filter_by(deleted=True).count())

#수정하기 루트
@app.route("/edit/<id>", methods=['POST'])
def edit(id):
	#입력받은 정보로 연락처를 수정
   edited=PERSON.query.get(id)
   edited.name=request.form['name']
   edited.number=request.form['number']
   edited.email=request.form['email']
   db.session.commit()
   return redirect("/")

#최근기록 루트
@app.route("/recent")
def recent():
	return render_template('recent.html', RECENT=RECENT.query.filter_by(deleted=False).all(), 
		ADDRESSBOOK=PERSON.query.filter_by(deleted=False).order_by("name").all(), contact_count=PERSON.query.filter_by(deleted=False).count(),
		trashcount=PERSON.query.filter_by(deleted=True).count())

if __name__ == "__main__" :
	app.run(debug=True)
