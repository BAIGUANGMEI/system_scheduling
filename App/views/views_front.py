from flask import Blueprint,render_template,request,redirect,session,url_for
from ..models.models_front import *

front = Blueprint('front', __name__)

@front.route('/schedulesystem/index/', methods=['GET', 'POST'])
def index():
    flag = False
    if session.get('user_id'):
        flag = True
    return render_template('front/front_index.html',flag=flag)

@front.route('/schedulesystem/introduction/', methods=['GET', 'POST'])
def introduction():
    flag = False
    if session.get('user_id'):
        flag = True
    return render_template('front/front_introduction.html',flag=flag)