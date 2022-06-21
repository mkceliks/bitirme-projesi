from flask import Flask, redirect, request, render_template,session,flash
from flask_login import LoginManager, login_required
from functools import wraps
from passlib.hash import pbkdf2_sha256
from flask_mongoengine import MongoEngine
from uuid import uuid4
import logging
app = Flask(__name__)
database_name = "API"
login_manager = LoginManager()
login_manager.init_app(app)


DB_URL ='mongodb+srv://admin:Jsz5AKtE7HPxIp2O@examscoring.k0pg0.mongodb.net/?retryWrites=true&w=majority'
app.config["MONGODB_HOST"]= DB_URL

logging.basicConfig(
    filename="logfile.txt",
    format="%(asctime)s - %(levelname)s - %(message)s ",
    filemode="w",
    level=logging.DEBUG)

logger = logging.getLogger()

db = MongoEngine()
db.init_app(app)


##########################################################
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user_email' in session:
            return f(*args, **kwargs)
        else:
            flash('Please login or signup first!')
            return redirect('/loginform')
    return wrap
##########################################################

def login_required_course(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        login_user = Roles.objects.get(role_name = session['user_role'])
        course_access = login_user.access
        if 'user_email' in session and "course" in course_access:
            return f(*args, **kwargs)
        else:
            flash('You are not able to see courses page!')
            return redirect(request.referrer)
    return wrap

def login_required_question(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        login_user = Roles.objects.get(role_name = session['user_role'])
        question_access = login_user.access
        if 'user_email' in session and "question" in question_access:
            return f(*args, **kwargs)
        else:
            flash('You are not able to see questions page!')
            return redirect(request.referrer)
    return wrap

def login_required_roles(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        login_user = Roles.objects.get(role_name = session['user_role'])
        roles_access = login_user.access
        if 'user_email' in session and "roles" in roles_access:
            return f(*args, **kwargs)
        else:
            flash('You are not able to see roles page!')
            return redirect(request.referrer)
    return wrap

def login_required_exams(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        login_user = Roles.objects.get(role_name = session['user_role'])
        exams_access = login_user.access
        if 'user_email' in session and "exams" in exams_access:
            return f(*args, **kwargs)
        else:
            flash('You are not able to see exams page!')
            return redirect(request.referrer)
    return wrap

def login_required_users(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        login_user = Roles.objects.get(role_name = session['user_role'])
        users_access = login_user.access
        if 'user_email' in session and "users" in users_access:
            return f(*args, **kwargs)
        else:
            flash('You are not able to see users page!')
            return redirect(request.referrer)
    return wrap

@app.route('/')
@login_required
def entry():
    return render_template('design.html')

@app.route('/index')
@login_required
def index():
    return render_template('design.html')
###########################################################

class Course(db.Document):
    course_id   = db.StringField()
    course_name = db.StringField()
    course_desc = db.StringField()
    course_date = db.StringField()
    course_term = db.StringField()
    
    def to_json(self):
        return {
                "course_id"   : self.course_id,
                "course_name" : self.course_name,
                "course_desc" : self.course_desc,
                "course_date" : self.course_date,
                "course_term" : self.course_term,
            }

@app.route('/courses', methods=["GET","POST"])
@login_required_course
def create_course():
    login_user = Roles.objects.get(role_name = session['user_role'])
    course_access = login_user.access
    if request.method == "GET":
        courses = []
        for course2 in Course.objects:
            courses.append(course2)
        if "full_access_course" in course_access:
            return render_template("full_access/courses.html",courses=courses)
        elif "limited_access_course" in course_access:
            return render_template("limited_access/courses.html",courses=courses)
    elif request.method == "POST":
        content = request.form
        new_course = Course(course_id=content['course_id'], 
                            course_name=content['course_name'], 
                            course_desc=content['course_desc'],
                            course_date=content['course_date'], 
                            course_term=content['course_term'])
        new_course.save()
        return redirect(request.referrer)


@app.route('/courses/<course_id>/delete', methods=["POST"])
@login_required_course
def delete_course(course_id):
    if request.method == "POST":
        course = Course.objects(course_id=course_id).first()
        course.delete()
        return redirect(request.referrer)


@app.route('/courses/<course_id>/update', methods=["GET","POST"])
@login_required_course
def update_course(course_id):
    if request.method == "GET":
        course = Course.objects(course_id=course_id).first()
        return render_template("course_edit.html",course=course)
    elif request.method == "POST":
        content = request.form
        updated_course = Course.objects(course_id=course_id).first()
        updated_course.course_id   = content['course_id']
        updated_course.course_name = content['course_name']
        updated_course.course_desc = content['course_desc']
        updated_course.course_date = content['course_date']
        updated_course.course_term = content['course_term']
        updated_course.save()
        return redirect('/courses')

@app.route('/courses/<course_id>/details', methods=["GET","POST"])
@login_required_course
def details_course(course_id):
    if request.method == "GET": 
        users = []
        for user2 in User.objects(user_course=course_id):
            users.append(user2)
        course = Course.objects(course_id=course_id).first()
        return render_template("course_details.html",course=course, users = users)

@app.route('/courses/<course_id>/details/adduser', methods=["GET","POST"])
@login_required_course
def adduser_course(course_id):
    if request.method == "GET":
        users = []
        for user2 in User.objects:
            users.append(user2)
        course = Course.objects(course_id=course_id).first()
        return render_template("course_adduser.html",users = users, course = course)
    elif request.method == "POST":
        content = request.form
        User.objects(user_name=content['course_id']).update_one(push__user_course=course_id)
        return redirect('/courses/{0}/details'.format(course_id))
    
@app.route('/courses/<course_id>/<user_number>/details/deluser', methods=["POST"])
@login_required_course
def deluser_course(course_id,user_number):
    if request.method == "POST":
        User.objects(user_number=user_number).update_one(pull__user_course=course_id)
        return redirect('/courses/{0}/details'.format(course_id))

    
##########################################################################
class Question(db.Document):
    question_id = db.StringField()
    exam = db.StringField()
    question = db.StringField()
    answer = db.StringField()
    alternative_answer1 = db.StringField()
    alternative_answer2 = db.StringField()
    question_score=db.IntField()
    
    
    def to_json(self):
        return {
                "question_id" : self.question_id,
                "exam" : self.exam,
                "question" : self.question,
                "answer" : self.answer,
                "alternative_answer1" : self.alternative_answer1,
                "alternative_answer2" : self.alternative_answer2,
                "question_score" : self.question_score
            }
    
    


@app.route('/questions', methods=["GET","POST"])
@login_required_question
def api_questions():
    login_user = Roles.objects.get(role_name = session['user_role'])
    course_access = login_user.access
    if request.method == "GET":
        questions = []
        exams= []
        for exam in Exam.objects:
            exams.append(exam)
        for questionn in Question.objects:
            questions.append(questionn)
        if "full_access_questions" in course_access:
            return render_template("full_access/questions.html",questions= questions,exams=exams)
        elif "limited_access_questions" in course_access:
            return render_template("limited_access/questions.html",questions= questions,exams=exams)
    elif request.method == "POST":
        content = request.form
        sentence=content['question']
        taking_answer=content['answer']
        sentence=sentence.replace(taking_answer,'______')
        question = Question(question_id=str(uuid4()), exam =content['exam'], 
                            question=sentence,answer=content['answer'],alternative_answer1=content['alternative_answer1'],alternative_answer2=content['alternative_answer2'],question_score=content['question_score'])
        question.save()
        logger.info("Soru oluşturuldu.")
        return redirect(request.referrer)
     

@app.route('/questions/<question_id>/delete', methods=["POST"])
@login_required_question
def delete_func(question_id):
    if request.method == "POST":
        question= Question.objects(question_id=question_id).first()
        question.delete()
        return redirect(request.referrer)
    
    
@app.route('/question/<question_id>/details', methods=["GET"])
@login_required_question
def question_details_func(question_id):
    if request.method == "GET": 
        question= Question.objects(question_id=question_id).first()
        sentence=question.question
        answer=question.answer
        sentence=sentence.replace('______',answer)
        question.question=sentence
        return render_template("question_details.html",question=question)
        


@app.route('/question/<question_id>/update', methods=["GET","POST"])
@login_required_question
def api_each_question(question_id):
    
    if request.method == "GET":
        exams= []
        for exam in Exam.objects:
            exams.append(exam)
        question= Question.objects(question_id=question_id).first()
        sentence=question.question
        answer=question.answer
        sentence=sentence.replace('______',answer)
        question.question=sentence
        return render_template("question_edit.html",question=question,exams=exams)
    
    elif request.method == "POST":
        content = request.form
        sentence=content['question']
        taking_answer=content['answer']
        sentence=sentence.replace(taking_answer,'______')
        updated_question= Question.objects(question_id=question_id).first()
        updated_question.exam = content['exam']
        updated_question.question = sentence
        updated_question.answer = content['answer']
        updated_question.alternative_answer1 = content['alternative_answer1']
        updated_question.alternative_answer2 = content['alternative_answer2']
        updated_question.question_score = content['question_score']
        updated_question.save()
        return redirect('/questions')
    
#######################################################################################

class User(db.Document):
    user_name   = db.StringField()
    user_surname = db.StringField()
    user_number = db.StringField()
    user_email = db.StringField()
    user_password = db.StringField()
    user_role = db.StringField()
    user_course = db.ListField(db.StringField())
    user_exam=db.ListField(db.StringField())
    ml_fall = db.ListField(db.StringField())
    
    def to_json(self):
        return {
                "user_name"   : self.user_name,
                "user_surname" : self.user_surname,
                "user_number" : self.user_number,
                "user_email" : self.user_email,
                "user_password" : self.user_password,
                "user_role" : self.user_role,
                "user_course" : self.user_course,
                "user_exam": self.user_exam,
                "ml_fall": self.ml_fall
            }
    
@app.route('/users',methods = ['GET','POST'])
@login_required_users
def create_user():
    login_user = Roles.objects.get(role_name = session['user_role'])
    course_access = login_user.access
    if request.method == "GET":       
        users = []
        roles = []
        for user2 in User.objects:
            users.append(user2)
        for user_roles in Roles.objects:
            roles.append(user_roles)
        if "full_access_users" in course_access:
            return render_template("full_access/users.html",users = users, roles=roles)
        elif "limited_access_users" in course_access:
            return render_template("limited_access/users.html",users = users, roles=roles)
    elif request.method == "POST":
        content = request.form
        new_user = User(user_name=content['user_name'], 
                        user_surname=content['user_surname'], 
                        user_number=content['user_number'],
                        user_email=content['user_email'],
                        user_password=pbkdf2_sha256.encrypt(content['user_password']),
                        user_role=content['user_role'])
        new_user.save()
        logger.info("Yeni kullanıcı oluşturuldu.")
        return redirect(request.referrer)
    
@app.route('/users/<user_number>/details', methods=["GET"])
@login_required_users
def details_user(user_number):
    if request.method == "GET": 
        roles = []
        for user_roles in Roles.objects:
            roles.append(user_roles)
        user = User.objects(user_number=user_number).first()
        return render_template("user_details.html",user=user,roles=roles)
        
@app.route('/users/<user_number>/delete', methods=["POST"])
@login_required_users
def delete_user(user_number):
    if request.method == "POST":
        user = User.objects(user_number=user_number).first()
        user.delete()
        return redirect(request.referrer)
    
@app.route('/users/<user_number>/update', methods=["GET","POST"])
@login_required_users
def update_user(user_number):
    if request.method == "GET":
        roles = []
        for user_roles in Roles.objects:
            roles.append(user_roles)
        user = User.objects(user_number=user_number).first()
        return render_template("user_edit.html",user=user,roles=roles)
    elif request.method == "POST":
        content = request.form
        updated_user = User.objects(user_number=user_number).first()
        updated_user.user_name = content['user_name']
        updated_user.user_surname = content['user_surname']
        updated_user.user_number = content['user_number']
        updated_user.user_email = content['user_email']
        if not (pbkdf2_sha256.verify(updated_user.user_password, pbkdf2_sha256.encrypt(content['user_password']))):          
            updated_user.user_password = pbkdf2_sha256.encrypt(content['user_password'])
        updated_user.user_role = content['user_role']
        updated_user.save()
        return redirect('/users')
    
#####################################################################################
class Exam(db.Document):
    exam_id   = db.StringField()
    exam_course = db.StringField()
    exam_name = db.StringField()
    exam_semester = db.StringField()
    exam_time = db.StringField()
    
    def to_json(self):
        return {
                "exam_id"   : self.exam_id,
                "exam_course" : self.exam_course,
                "exam_name" : self.exam_name,
                "exam_semester" : self.exam_semester,
                "exam_time" : self.exam_time,
            }
    
@app.route('/exams', methods=["GET","POST"])
@login_required_exams
def create_exam():
    login_user = Roles.objects.get(role_name = session['user_role'])
    course_access = login_user.access
    if request.method == "GET":
        exams = []
        courses=[]
        for course in Course.objects:
            courses.append(course)
        for exams2 in Exam.objects:
            exams.append(exams2)
        if "full_access_exams" in course_access:
            return render_template("full_access/exams.html",exams=exams , courses=courses)
        elif "limited_access_exams" in course_access:
            return render_template("limited_access/exams.html",exams=exams , courses=courses)
    elif request.method == "POST":
        content = request.form
        new_exam = Exam(exam_id=str(uuid4()), 
                          exam_course=content['exam_course'], 
                          exam_name=content['exam_name'],
                          exam_semester=content['exam_semester'],
                          exam_time=content['exam_time'])
        new_exam.save()
        logger.info("Yeni sınav oluşturuldu.")
        return redirect(request.referrer)
    
@app.route('/exams/<exam_id>/delete', methods=["POST"])
@login_required_exams
def delete_exama(exam_id):
    if request.method == "POST":
        exam = Exam.objects(exam_id=exam_id).first()
        exam.delete()
        return redirect(request.referrer)
    
@app.route('/exams/<exam_id>/update', methods=["GET","POST"])
@login_required_exams
def update_exam(exam_id):
    if request.method == "GET":
        exam = Exam.objects(exam_id = exam_id).first()
        return render_template("exam_edit.html",exam = exam)
    elif request.method == "POST":
        content = request.form
        updated_exam = Exam.objects(exam_no=exam_id).first()
        updated_exam.exam_course  = content['exam_course']
        updated_exam.exam_name = content['exam_name']
        updated_exam.exam_semester  = content['exam_semester']
        updated_exam.exam_time  = content['exam_time']
        updated_exam.save()
        return redirect('/exams')

@app.route('/exams/<exam_id>/enroll/adduser', methods=["GET","POST"])
@login_required_exams
def adduser_exam(exam_id):
    if request.method == "GET":
        users = []
        for user2 in User.objects:
            users.append(user2)
        exam = Exam.objects(exam_id=exam_id).first()
        return render_template("exam_adduser.html",users = users, exam = exam)
    elif request.method == "POST":
        content = request.form
        exam = Exam.objects(exam_id=exam_id).first()
        User.objects(user_name=content['exam_id']).update_one(push__user_exam=exam_id)
        return redirect('/exams/{0}/details'.format(exam_id))


@app.route('/exams/<exam_id>/<user_number>/enroll/deluser', methods=["POST"])
@login_required_exams
def deluser_exam(exam_id,user_number):
    if request.method == "POST":
        User.objects(user_number=user_number).update_one(pull__user_exam=exam_id)
        return redirect('/exams/{0}/details'.format(exam_id))

@app.route('/exams/<exam_id>/details', methods=["GET","POST"])
@login_required_exams
def details_exams(exam_id):
    if request.method == "GET": 
        exam = Exam.objects(exam_id = exam_id).first()
        users = []
        for user2 in User.objects(user_exam=exam_id):
            users.append(user2)
        return render_template("exam_details.html",exam=exam, users=users)
    

@app.route('/exams/<exam_id>/questions' , methods=["GET"])
@login_required_exams
def exam_questions(exam_id):
    if request.method == "GET":
        exam = Exam.objects(exam_id = exam_id).first()
        exam_name = exam.exam_name
        questions=[]
        for question in Question.objects(exam=exam_name):
            questions.append(question)
        return render_template("exam_questions.html",questions=questions)

@app.route('/exams/<exam_id>/evaluate' , methods=["GET"])
@login_required_exams
def exam_evaluate(exam_id):
    if request.method == "GET":
        exam = Exam.objects(exam_id = exam_id).first()
        users = []
        for user2 in User.objects(user_exam=exam_id):
            users.append(user2)
        exam_name = exam.exam_name
        questions=[]
        for question in Question.objects(exam=exam_name):
            questions.append(question)
        return render_template("exam_evaluate.html",questions=questions, users=users,exam=exam)
    
@app.route('/exams/<exam_id>/evaluate_students' , methods=["POST"])
@login_required_exams
def exam_evaluate_students(exam_id):
    if request.method == "POST":
        exam = Exam.objects(exam_id = exam_id).first()
        content = request.form
        users = User.objects(user_number = content['student_number']).first()
        user_answers = []
        for answers in users.ml_fall:
            user_answers.append(answers)
        exam_name = exam.exam_name
        questions=[]
        for question in Question.objects(exam=exam_name):
            questions.append(question)
        all_users = []
        for user2 in User.objects(user_exam=exam_id):
            all_users.append(user2)
        return render_template("exam_evaluate_student.html",questions=questions, users=users,exam=exam,user_answers=user_answers,all_users=all_users)    

@app.route('/exams/<exam_id>/evaluate_questions' , methods=["POST"])
@login_required_exams
def exam_evaluate_questions(exam_id):
    if request.method == "POST":
        exam = Exam.objects(exam_id = exam_id).first()
        all_answers = []
        for user in User.objects(user_exam =exam_id):
            all_answers.append(user.ml_fall)
        exam_name = exam.exam_name
        questions=[]
        for question in Question.objects(exam=exam_name):
            questions.append(question)
        content = request.form
        name = content['count']
        var = 0
        for i in range(len(questions)+1):
            if questions[i].question == name:
                    var = i
                    break 
        
        all_users = []
        for user2 in User.objects(user_exam=exam_id):
            all_users.append(user2)
        return render_template("exam_evaluate_questions.html",questions=questions,exam=exam,all_users=all_users,name=name,all_answers=all_answers,var=var)

@app.route('/exams/<exam_id>/score' , methods=["GET"])
@login_required_exams
def exam_score(exam_id):
    if request.method == "GET":
        exam = Exam.objects(exam_id = exam_id).first()
        all_answers = []
        for user in User.objects(user_exam =exam_id):
            all_answers.append(user.ml_fall)
        exam_name = exam.exam_name
        questions=[]
        for question in Question.objects(exam=exam_name):
            questions.append(question)
        all_users = []
        for user2 in User.objects(user_exam=exam_id):
            all_users.append(user2)
        score = []
        for j in range (len(all_users)):
            temp = 0
            for i in range(len(questions)):
                if questions[i].answer == all_answers[j][i] or questions[i].alternative_answer1 == all_answers[j][i] or questions[i].alternative_answer2 == all_answers[j][i]:
                    temp = temp + questions[i].question_score
            score.append(temp)
        return render_template("exam_score.html",questions=questions,exam=exam,all_users=all_users,all_answers=all_answers,score =score)    


####################################################################

@app.route('/loginform')
def loginform():
    if 'user_email' in session:
         flash('You already logged in.')
         return redirect('/index')
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        content = request.form
    login_user = User.objects.get(user_email=content['email'])
    if login_user:
        if pbkdf2_sha256.verify(content['password'],login_user['user_password']):
            session['user_email'] = content['email']
            session['user_role'] = login_user['user_role']
            return redirect('/index')
    flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_email', None)
    session.pop('user_role', None)
    flash('You were successfully logged out')
    return redirect('/loginform')

class Roles(db.Document):
    
    role_name   = db.StringField()
    access = db.ListField(db.StringField())

    def to_json(self):
        return {
                "role_name"   : self.role_name,
                "access" : self.access                
            }

@app.route('/roles', methods=['GET','POST'])
@login_required_roles
def roles():
    login_user = Roles.objects.get(role_name = session['user_role'])
    course_access = login_user.access
    if request.method == "GET":
        roles = []
        for user_roles in Roles.objects:
            roles.append(user_roles)
        if "full_access_roles" in course_access:
            return render_template("full_access/roles.html",roles = roles)
        elif "limited_access_roles" in course_access:
            return render_template("limited_access/roles.html",roles = roles)
    elif request.method == "POST":
        content = request.form
        new_role = Roles(role_name=content['role_name'])
        new_role.save()
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_1'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_2'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_3'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_4'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_5'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_6'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_7'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_8'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_9'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_10'])
        logger.info("Yeni rol oluşturuldu.")
        return redirect(request.referrer)

@app.route('/roles/<role_name>/details', methods=["GET"])
@login_required_roles
def details_role(role_name):
    if request.method == "GET": 
        users = []
        for user2 in User.objects(user_role=role_name):
            users.append(user2)
        role = Roles.objects(role_name=role_name).first()
        return render_template("roles_details.html",role=role, users=users)

@app.route('/roles/<role_name>/delete', methods=["POST"])
@login_required_roles
def delete_role(role_name):
    if request.method == "POST":
        role = Roles.objects(role_name=role_name).first()
        role.delete()
        return redirect(request.referrer)

@app.route('/roles/<role_name>/update', methods=["GET","POST"])
@login_required_roles
def update_role(role_name):
    if request.method == "GET":
        role = Roles.objects(role_name=role_name).first()
        return render_template("roles_edit.html",role=role)
    elif request.method == "POST":
        content = request.form
        updated_role = Roles.objects(role_name=role_name).first()
        updated_role2 = User.objects(user_role=role_name).first()
        updated_role.role_name = content['role_name']
        if updated_role2 != None:
            updated_role2.user_role = content['role_name']
            updated_role2.save()
        updated_role.save()       
        updated_role.update(pull_all__access = ['course','exams','question','users','roles','Null','full_access_roles','limited_access_roles','full_access_exams','limited_access_exams','full_access_questions','limited_access_questions','full_access_users','limited_access_users','full_access_course','limited_access_course'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_1'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_2'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_3'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_4'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_5'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_6'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_7'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_8'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_9'])
        Roles.objects(role_name=content['role_name']).update_one(push__access=content['access_10'])
        return redirect('/roles')


####################################################################



@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)
    
if __name__ == "__main__":
    app.secret_key = 'mysecret'
    app.run(debug=True)