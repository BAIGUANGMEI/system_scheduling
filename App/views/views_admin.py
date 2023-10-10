from flask import Blueprint,render_template,request,redirect,session,url_for
from ..models.models_admin import *

admin = Blueprint('admin', __name__)

@admin.route('/schedulesystem/admin/login/' , methods=['GET','POST'])
def login():
    flag = False
    if session.get('user_id'):
        flag = True
    if request.method =='POST':
        username=request.form.get('username')
        password=request.form.get('password')
        user = User.query.filter_by(username=username,password=password).first()
        try:
            if user == None:
                error = '用户名或密码错误'
                return redirect("/schedulesystem/admin/login/")
            else:
                session['user_id'] = user.id
                return redirect("/schedulesystem/index")
        except Exception as e:
            return 'add user fail' + str(e)
    elif request.method =='GET':
        return render_template('/admin/admin_login.html',flag=flag)

@admin.route('/schedulesystem/admin/register/',methods=['GET','POST'])
def register():
    flag = False
    if session.get('user_id'):
        flag = True
    if request.method =='GET':
        return render_template('/admin/admin_register.html',flag=flag)
    else:
        username=request.form.get('username')
        password=request.form.get('password')
        confirm=request.form.get('confirm')
        un = User.query.filter_by(username=username).first()
        user = User(username=username,password=password)
        try:
            if password == confirm and un == None:
                db.session.add(user)
                db.session.commit()
                return redirect('/schedulesystem/index/')
            elif username != None:
                error = '用户名已存在'
                return render_template('/admin/admin_register.html',flag=flag)
            else:
                error = '密码不一致'
                return render_template('/admin/admin_register.html',flag=flag)
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            return 'add user fail' + str(e)

@admin.route('/schedulesystem/admin/logout/')
def logout():
    session.clear()
    return redirect('/schedulesystem/index/')