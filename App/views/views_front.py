from flask import Blueprint, render_template, request, redirect, session, url_for
from ..models.models_front import *
from ..models.models_admin import *

front = Blueprint('front', __name__)


# 网站首页接口
@front.route('/schedulesystem/index/', methods=['GET', 'POST'])
def index():
    flag = False
    if session.get('user_id'):
        flag = True
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    return render_template('front/front_index.html', flag=flag, user=user)


# 门店信息界面接口
@front.route('/schedulesystem/introduction/', methods=['GET', 'POST'])
def introduction():
    flag = False
    if session.get('user_id'):
        flag = True
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    return render_template('front/front_introduction.html', flag=flag, user=user)

# 门店信息界面客流量数据接口
@front.route('/schedulesystem/introduction/graph/', methods=['GET'])
def graph():
    return {'code': 200, 'data_morning': [5, 20, 36, 10, 10, 20,10],
            'data_afternoon':[7, 21, 16, 10, 10, 20,20],
            'data_evening':[46, 30, 36, 45, 25, 70,33]}
