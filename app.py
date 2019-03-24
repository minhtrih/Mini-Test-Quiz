# Importing Files
from flask import Flask, render_template, request, redirect, session, url_for,Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, BooleanField, SubmitField,RadioField
from wtforms.validators import InputRequired, Length
import random
from plotly.offline import plot
from plotly.graph_objs import Scatter
from datetime import datetime
from xml.sax import saxutils as su


# Initializing global variables
app = Flask(__name__)
app.config['SECRET_KEY']= 'this is a super secure kry'
app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+pymysql://root:minhtrih@127.0.0.1/test_quiz'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, nullable=False, primary_key=True, unique=True)
    name = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
	

def __init__(self, name, password):
	self.name = name
	self.password = password


class Question(db.Model):
	__tablename__ = 'question'
	id = db.Column(db.Integer, nullable=False, primary_key=True, unique=True)
	question = db.Column(db.String(), nullable=False)
	correct = db.Column(db.String(8), nullable=False)
	answera = db.Column(db.String(256))
	answerb = db.Column(db.String(256))
	answerc = db.Column(db.String(256))
	answerd = db.Column(db.String(256))
	answere = db.Column(db.String(256))
	description = db.Column(db.String())
	code = db.Column(db.String())
	keyword = db.Column(db.String(), nullable=False)
	language = db.Column(db.Integer(), nullable=False)
	order = db.Column(db.Integer())
	asked = db.Column(db.Integer())
	answered = db.Column(db.Integer())
	nextqid = db.Column(db.Integer(), nullable=False)
	author = db.Column(db.String())
	userid = db.Column(db.Integer(), nullable=False)


	def __init__(self, question, correct, answera, answerb, answerc, answerd, answere, description, 
							code, keyword, language, order, asked, answered, nextqid, author, userid):
		self.question = question
		self.correct = correct
		self.answera = answera
		self.answerb = answerb
		self.answerc = answerc
		self.answerd = answerd
		self.answere = answere
		self.description = description
		self.code = code
		self.keyword = keyword
		self.language = language
		self.order = order
		self.asked = asked
		self.answered = answered
		self.nextqid = nextqid
		self.author = author
		self.userid = userid


class Language(db.Model):
	__tablename__ = 'language'
	id = db.Column(db.Integer, nullable=False, primary_key=True, unique=True)
	language = db.Column(db.String(32), nullable=False)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


a,b,c,d = '','','',''
correct_ans = []
given_ans = []


# For making different user objects
class SignupForm(FlaskForm):
	username = TextField('username',validators=[InputRequired()])
	password = PasswordField('password',validators=[InputRequired(), Length(min=3, max=16)])
	choice = RadioField('Answer', choices=[(a,'A'),(b,'B'),(c,'C'),(d,'D')])


@app.route('/signup', methods=['POST','GET'])
@app.route('/')
def index():
	form = SignupForm()
	msg = ''
	if request.method == 'POST':
		search = User.query.filter_by(name=form.username.data).first()
		if search:
			msg = 'Username already exists'
		else:
			new_user = User(name=form.username.data, password=form.password.data)
			db.session.add(new_user)
			db.session.commit()
			login_user(new_user)
			return redirect(url_for('login'))

	return render_template('signup.html', form=form, msg=msg)


@app.route('/login', methods=['POST','GET'])
def login():
	form = SignupForm()
	msg = 'Invalid Username or Password'
	if request.method == 'POST':
		search = User.query.filter_by(name=form.username.data).first()
		if search:
			authu = search.name
			authp = search.password
			if authu == form.username.data and authp == form.password.data:
				login_user(search)
				session['name'] = form.username.data
				return redirect(url_for('trivia', name=authu))
		
		return render_template('index.html', msg=msg, form=form)

	return render_template('index.html', form=form)


@app.route('/trivia')
@app.route('/trivia/<name>')
@login_required
def trivia(name):
	category = []
	category_id = []
	language = Language.query.all()
	if language is not None:
		for i in range(7):
			category.append(language[i].language)
			category_id.append(language[i].id)
	return render_template('categories.html',category=category,category_id=category_id)

@app.route('/question/<id_name>' ,methods=['POST','GET'])
@login_required
def question(id_name):
	form = SignupForm()
	quest = []
	correct_ans.clear()
	given_ans.clear()
	incorrct_ans = []
	code = []
	question = Question.query.filter_by(language=id_name).all()
	m = len(question)
	n = range(len(question))
	for i in n:
		if question[i].code is not None:
			code.append(su.unescape(question[i].code))
		else:
			code.append(' ')

		incorrect_answers = []
		if question[i].correct == 'a':
			correct_ans.append(su.unescape(question[i].answera))
			incorrect_answers.append(question[i].answerb)
			incorrect_answers.append(question[i].answerc)
			incorrect_answers.append(question[i].answerd)
			incorrect_answers.append(question[i].answere)
		if question[i].correct == 'b':
			correct_ans.append(su.unescape(question[i].answerb))
			incorrect_answers.append(question[i].answera)
			incorrect_answers.append(question[i].answerc)
			incorrect_answers.append(question[i].answerd)
			incorrect_answers.append(question[i].answere)
		if question[i].correct == 'c':
			correct_ans.append(su.unescape(question[i].answerc))
			incorrect_answers.append(question[i].answera)
			incorrect_answers.append(question[i].answerb)
			incorrect_answers.append(question[i].answerd)
			incorrect_answers.append(question[i].answere)
		if question[i].correct == 'd':
			correct_ans.append(su.unescape(question[i].answerd))
			incorrect_answers.append(question[i].answera)
			incorrect_answers.append(question[i].answerb)
			incorrect_answers.append(question[i].answerc)
			incorrect_answers.append(question[i].answere)
		if question[i].correct == 'e':
			correct_ans.append(su.unescape(question[i].answere))
			incorrect_answers.append(question[i].answera)
			incorrect_answers.append(question[i].answerb)
			incorrect_answers.append(question[i].answerc)
			incorrect_answers.append(question[i].answerd)
		quest.append(question[i].question)
		incorrct_ans.append(incorrect_answers)
	options = []
	choices = []
	for i in n:
		options.append([correct_ans[i]])
		# options.append([incorrct_ans[i]])
		for j in range(4):
			if incorrct_ans[i][j] is not None:
				options[i].append(su.unescape((incorrct_ans[i][j])))
		choices.append(len(options[i]))	
	for i in n:
		random.shuffle(options[i])

	return render_template('questions.html',quest=quest,correct_ans=correct_ans,options=options, form=form, n=n, m=m, choices=choices, code=code)


@app.route('/result/<m>',methods=['POST'])
def result(m):
	count = 0
	new = []
	n = range(int(m))
	draw_map = []
	for i in n:
		draw_map.append(i+1)
		try:
			given_ans.append(request.form[str(i)]) 
			if request.form[str(i)]==correct_ans[i]:
				count+=1
				new.append(1)
			else:
				new.append(0)
		except:
			given_ans.append(' ') 
			new.append(0)
	answer = len(draw_map)
	msg = ''
	if count<3:
		msg="Poor Result...Shame on You"
	elif count>8:
		msg="Excellent Result...Your Parents Must Be Proud"
	else:
		msg = "NICE ONE"
	p = plot([Scatter(x=draw_map, y=new )],output_type="div")
	return render_template('result.html',count=count,given_ans=given_ans,correct_ans=correct_ans,msg=msg,div_placeholder=Markup(p), answer=answer)

@app.route('/navbar')
def navbar():
	return render_template('navbar.html')

@app.route('/cards')
def cards():
	return render_template('cards.html')

@app.route('/logout')
def logout():
	session['username'] = None
	logout_user()
	return redirect(url_for('login'))

if __name__ == '__main__':
	app.secret_key= 'confidential'
	app.run(debug=True)