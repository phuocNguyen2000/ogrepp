from flask import Flask,render_template,request,flash
from flask_cors import CORS, cross_origin
from flask.globals import session

from  form import SignUpForm,SignInForm,FormTask,FormProject,SearchForm
from werkzeug.utils import redirect
import  json
from flask_sqlalchemy import SQLAlchemy
from  flask_migrate import Migrate
import os
from datetime import datetime, date

# pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org <package_name>
basedir=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS '] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(basedir,'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = 'any string works here'
db=SQLAlchemy(app)
migrate=Migrate(app,db)

import models
@app.route('/')
@cross_origin(origin='*')
def login_process():
    todolist = [
        {
            'name': 'Đi học',
            'description': 'BVU'
        },
        {
            'name': 'Về nhà',
            'description': 'hasagi'
        }
    ]

    return render_template('index.html', todolist=todolist)

@app.route('/signUp', methods=['GET' , 'POST'])
@cross_origin(origin='*')
def sign_up():
    form=SignUpForm()
    if form.validate_on_submit():
        _fname = form.inputFirstName.data
        _lname = form.inputLastName.data
        _email = form.inputEmail.data
        _password = form.inputPassword.data
        if (db.session.query(models.User).filter_by(email=_email).count() == 0):
            _user = models.User(first_name=_fname, last_name=_lname, email=_email)
            _user.set_password(_password)
            db.session.add(_user)
            db.session.commit()
            return render_template('signup_success.html', user=_user)
        else:
            flash('Email {} is alrealy exsits!'.format(_email))
            return render_template('signup.html', form=form)

    return render_template('signup.html',form=form)

@app.route('/signIn', methods=['GET', 'POST'])
def SignIn():
    form = SignInForm()
    if form.validate_on_submit():
        _email = form.inputEmail.data
        _password = form.inputPassword.data

        user = db.session.query(models.User).filter_by(email = _email).first()
        if (user is None):
            flash('Sai Email hoặc mật khẩu!')
        else:
            if(user.check_password(_password)):

                session['user'] = user.user_id
                return redirect('/userHome')
            else:
                flash('Sai Email hoặc mật khẩu!')
    return render_template('signin.html', form = form)

@app.route('/addTodo/<int:projectId>', methods=['GET', 'POST'])
def AddTodo(projectId):
    _user_id = session.get('user')
    if _user_id:
        priorytys=models.Priority.query.all()
        priarr=[]
        for pri in priorytys:
            print(pri.description)
            priarr.append((pri.priority_id,pri.description))

        form = FormTask()
        form.inputPriority.choices=priarr
        print(priarr)
        user = db.session.query(models.User).filter_by(user_id = _user_id).first()
        
        project = db.session.query(models.Project).filter_by(project_id = projectId).first()
        print(project.project_id)
       
        if form.validate_on_submit():
            id=request.form['taskId']
           
            des = form.inputTask.data
            print(id,"ne2 id")
            if id=="0":       
                task=models.Task(description=des,project=project,priority_id=form.inputPriority.data,deadline=form.inputProjectDeadline.data)
                db.session.add(task)
                
            else:         
                 task = db.session.query(models.Task).filter_by(task_id = id).first()         
                 print(task)
                 task.description= des
                 task.project_id=project_id
                 task.priority_id=form.inputPriority.data
                 task.deadline=form.inputProjectDeadline.data
            if(task.deadline>project.deadline.date()):
                flash('Ehe chọn ngày khác đi bro')  
            else:
                db.session.commit()
                return redirect('/userTask')
        return render_template('usertodo.html',form = form,user=user,project=project)
    return redirect('/')

@app.route('/addProject', methods=['GET', 'POST'])
def addProject():
    _user_id = session.get('user')
    if _user_id:
        status=models.Status.query.all()
        form = FormProject()
       
        user = db.session.query(models.User).filter_by(user_id = _user_id).first()
       
        if form.validate_on_submit():
            id=request.form['projectId']
            des = form.inputProject.data
            print(id,"ne2 id")
            if id=="0":       
                project=models.Project(description=des,user=user,deadline=form.inputProjectDeadline.data)
                db.session.add(project)
                
            else:         
                 project = db.session.query(models.Project).filter_by(project_id = id).first()
                 print(project)
                 project.description= des
                 project.deadline=form.inputProjectDeadline.data
            db.session.commit()
            return redirect('/userHome')
        return render_template('userproject.html',form = form,user=user)
    return redirect('/')



@app.route('/userHome', methods=['GET', 'POST'])
def userHome():
    print('long ngu')
    _user_id = session.get('user')
    form=SearchForm()
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id = _user_id).first()
        g=[]
        if form.validate_on_submit():
            if form.inputSearch.data:
                for i in user.projects:
                    if form.inputSearch.data in i.description:
                        g.append(i)
                user.projects=g
            else:
                user = db.session.query(models.User).filter_by(user_id = _user_id).first()


        return render_template('userhome.html', user = user ,form=form)
    else:
        return redirect('/')

@app.route('/userTask', methods=['GET', 'POST'])
def userTask():
    print('long ngu')
    _user_id = session.get('user')
    id=request.form['projectId']
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id = _user_id).first()
        project = db.session.query(models.Project).filter_by(project_id=id).first()

        return render_template('usertask.html', user = user,project=project)
    else:
        return redirect('/')

@app.route('/completeTask', methods=['GET', 'POST'])
def completeTask():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id = _user_id).first()
        
        id=request.form['taskId']
        task = db.session.query(models.Task).filter_by(task_id = id).first()
        project=db.session.query(models.Project).filter_by(project_id = task.project_id).first()
        project.status_id=4
        for t in project.tasks:
            if t.is_completed==False:
                project.status_id=2
        print(task)
        task.is_completed= True
        db.session.commit()
        return render_template('usertask.html', project = project)
    else:
        return redirect('/')

@app.route('/logOut', methods=['GET', 'POST'])
def logOut():
    session.pop('user',None)
    return redirect('/signIn')

@app.route('/deleteTask', methods=['GET', 'POST'])
def deleteTask():
    _user_id = session.get('user')
    if _user_id:
        task_id= request.form['taskId']
        task = db.session.query(models.Task).filter_by(task_id = task_id).first()
        db.session.delete(task)
        db.session.commit()
        return redirect('/userHome')    
    else:
        return redirect('/')

@app.route('/deleteProjcet', methods=['GET', 'POST'])
def deleteProject():
    _user_id = session.get('user')
    if _user_id:
        project_id= request.form['projectId']
        project = db.session.query(models.Project).filter_by(project_id = project_id).first()
        db.session.delete(project)
        db.session.commit()
        return redirect('/userHome')
        
    else:
        return redirect('/')

@app.route('/editTask', methods=['GET', 'POST'])
def editTask():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id = _user_id).first()
        priorytys=models.Priority.query.all()
        priarr=[]
        for pri in priorytys:
            print(pri.description)
            priarr.append((pri.priority_id,pri.description))

        form = FormTask()
        form.inputPriority.choices=priarr

        task_id= request.form['taskId']
        task = db.session.query(models.Task).filter_by(task_id = task_id).first()
        form.inputPriority.default=task.priority_id
        form.inputProjectDeadline.default=task.deadline
        form.inputTask.default=task.description
        form.process()
        return render_template('usertodo.html', form = form,user=user,project=task.project)
        
    else:
        return redirect('/')

@app.route('/editProject', methods=['GET', 'POST'])
def editProject():
    _user_id = session.get('user')
    if _user_id:
        user = db.session.query(models.User).filter_by(user_id = _user_id).first()
        

        form = FormProject()


        project_id= request.form['projectId']
        project = db.session.query(models.Project).filter_by(project_id = project_id).first()
        form.inputProjectDeadline.default=project.deadline
        form.inputProject.default=project.description
        form.process()
        return render_template('userproject.html', form = form,user=user,project=project)
        
    else:
        return redirect('/')


@app.route('/auth', methods=['POST'])
@cross_origin(origin='http://localhost:3000')
def Auth():
    data = request.get_json()
    print(request.get_json())
    print("data Request:", data['email'])


    user = db.session.query(models.User).filter_by(email=data['email']).first()
    if (user is None):
        return json.dumps([{"message":"none"}])
    else:
        if (user.check_password(data["password"])):

            session['user'] = user.user_id
            s={"email" : user.email,"password" : user.password}
            print("ok")

            return json.dumps(s)
        else:
            return json.dumps([{"message":"sai email hoặc mật khẩu"}])

    return "s"

if __name__ == '__main__':
    app.run(debug=True)




