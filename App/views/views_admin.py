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
                return redirect("/schedulesystem/admin/login/",flag=flag)
            else:
                session['user_id'] = user.id
                return redirect("/schedulesystem/index",flag=flag)
        except Exception as e:
            return 'add user fail' + str(e)
    elif request.method =='GET':
        return render_template('/admin/admin_login.html',flag=flag)