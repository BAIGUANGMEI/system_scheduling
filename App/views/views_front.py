from flask import Blueprint, render_template, request, redirect, session
import pandas as pd
from ..models.models_front import *
from ..models.models_admin import *
from ..Algorithm.SA import *

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


@front.route('/schedulesystem/schedule', methods=['GET', 'POST'])
def schedule():
    flag = False
    if session.get('user_id'):
        flag = True
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    schedule = History.query.order_by(History.time.desc()).first()
    timelist = ['d1_morning', 'd1_afternoon', 'd1_evening',
                'd2_morning', 'd2_afternoon', 'd2_evening',
                'd3_morning','d3_afternoon', 'd3_evening',
                'd4_morning', 'd4_afternoon', 'd4_evening',
                'd5_morning', 'd5_afternoon','d5_evening',
                'd6_morning', 'd6_afternoon', 'd6_evening',
                'd7_morning', 'd7_afternoon', 'd7_evening']
    timelist2 = ['day1time1', 'day1time2', 'day1time3',
                    'day2time1', 'day2time2', 'day2time3',
                    'day3time1', 'day3time2', 'day3time3',
                    'day4time1', 'day4time2', 'day4time3',
                    'day5time1', 'day5time2', 'day5time3',
                    'day6time1', 'day6time2', 'day6time3',
                    'day7time1', 'day7time2', 'day7time3']
    final_schedule = {}
    for i in range(len(timelist)):
        list = ''
        example=getattr(schedule,timelist[i])
        for j in range(len(example)):
            if '0' <= example[j] <= '9':
                staff = Staff.query.filter_by(id=int(example[j]) + 1).first()
                list+=staff.name+' '
        final_schedule[timelist2[i]] = list
    return render_template('front/front_scheduledaily.html', flag=flag, user=user, schedule=final_schedule)


@front.route('/schedulesystem/staff/', methods=['GET', 'POST'])
def staff():
    flag = False
    if session.get('user_id'):
        flag = True
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    staffs = Staff.query.all()
    return render_template('front/front_staff.html', flag=flag, user=user, staffs=staffs)


@front.route('/schedulesystem/staff/detail', methods=['GET', 'POST'])
def staff_detail():
    if request.method == "GET":
        staff_id = request.args.get('sid')
        staff = Staff.query.filter_by(id=staff_id).first()
        return render_template('front/front_staff_details.html', staff=staff)
    else:
        return redirect('/schedulesystem/staff/')


@front.route('/schedulesystem/staff/add', methods=['GET', 'POST'])
def staff_add():
    if request.method == "GET":
        return render_template('front/front_staff_add.html')
    else:
        staff_name = request.form.get('staffname')
        staff_birthyear = request.form.get('staffbirthyear')
        staff_gender = request.form.get('staffgender')
        staff_workyear = request.form.get('staffworkyear')
        staff = Staff(name=staff_name, gender=staff_gender, birthyear=staff_birthyear, workyear=staff_workyear)
        try:
            db.session.add(staff)
            db.session.commit()
            return redirect('/schedulesystem/staff/')
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            return 'add staff fail' + str(e)


@front.route('/schedulesystem/about/', methods=['GET', 'POST'])
def about():
    flag = False
    if session.get('user_id'):
        flag = True
    user_id = session.get('user_id')
    user = User.query.filter_by(id=user_id).first()
    return render_template('front/front_about.html', flag=flag, user=user)


# 门店信息界面客流量数据接口
@front.route('/schedulesystem/introduction/graph/', methods=['GET'])
def graph():
    return {'code': 200, 'data_morning': [5, 20, 36, 10, 10, 20, 10],
            'data_afternoon': [7, 21, 16, 10, 10, 20, 20],
            'data_evening': [46, 30, 36, 45, 25, 70, 33]}


# 门店排班信息接口（按周查看）
@front.route('/schedulesystem/schedule/daily/', methods=['GET', 'POST'])
def schedule_daily():
    ans = calculate('/Users/baiguang/PycharmProjects/ScheduleSystem/App/Algorithm/data.xlsx',
                    '/Users/baiguang/PycharmProjects/ScheduleSystem/App/Algorithm/data2.xlsx')
    schedule = transform_day(ans)
    print(schedule)
    sche = History(d1_morning=str(schedule['day1time1']), d1_afternoon=str(schedule['day1time2']),d1_evening=str(schedule['day1time3']),
                    d2_morning=str(schedule['day2time1']), d2_afternoon=str(schedule['day2time2']),d2_evening=str(schedule['day2time3']),
                    d3_morning=str(schedule['day3time1']), d3_afternoon=str(schedule['day3time2']),d3_evening=str(schedule['day3time3']),
                    d4_morning=str(schedule['day4time1']), d4_afternoon=str(schedule['day4time2']),d4_evening=str(schedule['day4time3']),
                    d5_morning=str(schedule['day5time1']), d5_afternoon=str(schedule['day5time2']),d5_evening=str(schedule['day5time3']),
                    d6_morning=str(schedule['day6time1']), d6_afternoon=str(schedule['day6time2']),d6_evening=str(schedule['day6time3']),
                    d7_morning=str(schedule['day7time1']), d7_afternoon=str(schedule['day7time2']),d7_evening=str(schedule['day7time3']))
    db.session.add(sche)
    db.session.commit()
    schedule = History.query.order_by(History.time.desc()).first()
    timelist = ['d1_morning', 'd1_afternoon', 'd1_evening',
                'd2_morning', 'd2_afternoon', 'd2_evening',
                'd3_morning','d3_afternoon', 'd3_evening',
                'd4_morning', 'd4_afternoon', 'd4_evening',
                'd5_morning', 'd5_afternoon','d5_evening',
                'd6_morning', 'd6_afternoon', 'd6_evening',
                'd7_morning', 'd7_afternoon', 'd7_evening']
    timelist2 = ['day1time1', 'day1time2', 'day1time3',
                    'day2time1', 'day2time2', 'day2time3',
                    'day3time1', 'day3time2', 'day3time3',
                    'day4time1', 'day4time2', 'day4time3',
                    'day5time1', 'day5time2', 'day5time3',
                    'day6time1', 'day6time2', 'day6time3',
                    'day7time1', 'day7time2', 'day7time3']
    final_schedule = {}
    for i in range(len(timelist)):
        list = []
        example=getattr(schedule,timelist[i])
        for j in range(len(example)):
            if '0' <= example[j] <= '9':
                staff = Staff.query.filter_by(id=int(example[j]) + 1).first()
                list.append(staff.name)
        final_schedule[timelist2[i]] = list
    return final_schedule
