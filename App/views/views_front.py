from flask import Blueprint, render_template, request, redirect, session
import pandas as pd
from ..models.models_front import *
from ..models.models_admin import *
from ..Algorithm.SA import *
from ..Algorithm.Leave import *
from ..Global_component.DataBaseStatus import DataBaseStatus

front = Blueprint('front', __name__)

timelist = ['d1_morning', 'd1_afternoon', 'd1_evening',
            'd2_morning', 'd2_afternoon', 'd2_evening',
            'd3_morning', 'd3_afternoon', 'd3_evening',
            'd4_morning', 'd4_afternoon', 'd4_evening',
            'd5_morning', 'd5_afternoon', 'd5_evening',
            'd6_morning', 'd6_afternoon', 'd6_evening',
            'd7_morning', 'd7_afternoon', 'd7_evening']
timelist2 = ['day1time1', 'day1time2', 'day1time3',
             'day2time1', 'day2time2', 'day2time3',
             'day3time1', 'day3time2', 'day3time3',
             'day4time1', 'day4time2', 'day4time3',
             'day5time1', 'day5time2', 'day5time3',
             'day6time1', 'day6time2', 'day6time3',
             'day7time1', 'day7time2', 'day7time3']

dbstatus = DataBaseStatus()

def if_login():
    # 判断是否登录
    flag = False
    if session.get('user_id'):
        flag = True
    user_id = session.get('user_id')
    return flag, user_id

# 网站首页接口
@front.route('/schedulesystem/index/', methods=['GET', 'POST'])
def index():
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    return render_template('front/front_index.html', flag=flag, user=user)


# 门店信息界面接口
@front.route('/schedulesystem/introduction/', methods=['GET', 'POST'])
def introduction():
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    return render_template('front/front_introduction.html', flag=flag, user=user)

# 排班情况的接口(按周查看)
@front.route('/schedulesystem/schedule', methods=['GET', 'POST'])
def schedule():
    status = dbstatus.isChange
    # print(dbstatus.isChange)
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    # 从数据库中查询最新的排班信息
    schedule = History.query.order_by(History.time.desc()).first()
    final_schedule = {}
    try:
        # 排班数据的字符处理
        for i in range(len(timelist)):
            list = []
            example=getattr(schedule,timelist[i])
            example=example.replace('[','')
            example=example.replace(']','')
            example=example.split(',')
            # 从数据库中查询员工信息
            for j in range(len(example)):
                staff = Staff.query.filter_by(id=int(example[j]) + 1).first()
                list.append(staff.name)
            final_schedule[timelist2[i]] = str(list).replace('[','').replace(']','').replace('\'','')
    # 异常处理
    except Exception as e:
        print(e)
        final_schedule = {}
    return render_template('front/front_scheduledaily.html', flag=flag, user=user, schedule=final_schedule,status=status)

# 排班情况的接口（按员工查看）
@front.route('/schedulesystem/schedulestaff', methods=['GET', 'POST'])
def schedule_s():
    status = dbstatus.isChange
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    # 从数据库中查找最新的数据
    schedule = History.query.order_by(History.time.desc()).first()
    staff = Staff.query.all()
    final_schedule = {}
    staff_name = []
    id_list = Staff.query.with_entities(Staff.id).all()
    id_list = [i[0] for i in id_list]
    try:
        for i in staff:
            final_schedule[str(i.id)]=[0 for k in range(21)]
            staff_name.append(i.name)
        # 排班数据的字符处理
        for i in range(len(timelist)):
            example=getattr(schedule,timelist[i])
            example=example.replace('[','')
            example=example.replace(']','')
            example=example.split(',')
            for j in example:
                final_schedule[str(int(j)+1)][i] = 1
        change_info = getattr(schedule,'change')
        if change_info != None:
            change_info = change_info.replace('[','').replace(']','').split(',')
            leave_info = [id_list.index(int(change_info[0])+1),int(change_info[1]),int(change_info[2]),int(change_info[3])]
            change_info = [id_list.index(int(change_info[4])+1),int(change_info[5]),int(change_info[6]),int(change_info[7])]
            # print(leave_info,change_info)
            index_leave = 3*leave_info[1] + leave_info[2]
            index_change = 3*change_info[1] + change_info[2]
            final = {}
            for i in range(len(id_list)):
                final[staff_name[i]] = final_schedule[str(id_list[i])]
            final[staff_name[leave_info[0]]][index_leave] = leave_info[3]
            final[staff_name[change_info[0]]][index_change] = change_info[3]
            # print(final)
        else:
            final = {}
            for i in range(len(staff_name)):
                final[staff_name[i]] = final_schedule[str(id_list[i])]
    # 异常处理
    except Exception as e:
        # print(e)
        final_schedule = {}
        return "error"
    return render_template('front/front_schedulestaff.html', flag=flag, user=user, final_schedule=final,status=status)

#员工请求处理接口
@front.route('/schedulesystem/staff/request', methods=['GET', 'POST'])
def staff_request():
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    # 返回员工的请求信息
    staff_request = Staff_request.query.all()
    return render_template('front/staff/front_staff_request.html', flag=flag, user=user, staff_request=staff_request)

# 员工信息界面的接口
@front.route('/schedulesystem/staff/', methods=['GET', 'POST'])
def staff():
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    # 查询所有员工的信息
    staffs = Staff.query.all()
    return render_template('front/staff/front_staff.html', flag=flag, user=user, staffs=staffs)

#员工详情界面的接口
@front.route('/schedulesystem/staff/detail', methods=['GET', 'POST'])
def staff_detail():
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    # GET请求，获取员工id，查询员工信息
    if request.method == "GET":
        staff_id = request.args.get('sid')
        staff = Staff.query.filter_by(id=staff_id).first()
        return render_template('front/staff/front_staff_details.html', staff=staff, flag=flag, user=user)
    # POST请求，返回员工信息界面
    else:
        return redirect('/schedulesystem/staff/')

# 员工信息修改的接口
@front.route('/schedulesystem/staff/modify', methods=['GET', 'POST'])
def staff_modify():
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    # GET请求，获取员工id，查询员工信息
    if request.method == "GET":
        staff_id = request.args.get('sid')
        staff = Staff.query.filter_by(id=staff_id).first()
        return render_template('front/staff/front_staff_modify.html', staff=staff, flag=flag, user=user)
    else:
        staff_id = request.form.get('staffid')
        staff_name = request.form.get('staffname')
        staff_birthyear = request.form.get('staffbirthyear')
        staff_gender = request.form.get('staffgender')
        staff_workyear = request.form.get('staffworkyear')
        staff_daylike = request.form.getlist('daylike')
        staff_timelike = request.form.getlist('timelike')
        # print(staff_name, staff_birthyear,staff_gender,staff_workyear,staff_daylike,staff_timelike)
        staff = Staff.query.filter_by(id=staff_id).first()
        if staff_name != '':
            staff.name = staff_name
        if staff_birthyear != '':
            staff.birthyear = staff_birthyear
        if staff_gender == 0:
            staff.gender = 'male'
        else:
            staff.gender = 'female'
        if staff_workyear != '':
            staff.workyear = staff_workyear

        if staff_daylike == []:
            pass
        elif staff_daylike[0] == '7':
            staff.daylike = None
        else:
            for i in range(len(staff_daylike)):
                staff_daylike[i] = int(staff_daylike[i])
            staff.daylike = str(staff_daylike)
        if staff_timelike == []:
            pass
        elif staff_timelike[0] =='3':
            staff.timelike = None
        else:
            for i in range(len(staff_timelike)):
                staff_timelike[i] = int(staff_timelike[i])
            staff.timelike = str(staff_timelike)
        db.session.commit()
        dbstatus.changestatus(True)
        print(dbstatus.isChange)
        return redirect('/schedulesystem/staff/')


# 增加员工的接口
@front.route('/schedulesystem/staff/add', methods=['GET', 'POST'])
def staff_add():
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    # GET请求，返回增加员工界面
    if request.method == "GET":
        return render_template('front/staff/front_staff_add.html', flag=flag, user=user)
    # POST请求，增加员工
    else:
        staff_name = request.form.get('staffname')
        staff_birthyear = request.form.get('staffbirthyear')
        staff_gender = request.form.get('staffgender')
        staff_workyear = request.form.get('staffworkyear')
        staff_daylike = request.form.getlist('daylike')
        staff_timelike = request.form.getlist('timelike')
        print(staff_name, staff_birthyear,staff_gender,staff_workyear,staff_daylike,staff_timelike)
        if staff_name == '':
            return "Please input the name"
        if staff_daylike == []:
            staff_daylike = None
        else:
            for i in range(len(staff_daylike)):
                staff_daylike[i] = int(staff_daylike[i])
            staff_daylike = str(staff_daylike)
        if staff_timelike == []:
            staff_timelike = None
        else:
            for i in range(len(staff_timelike)):
                staff_timelike[i] = int(staff_timelike[i])
            staff_timelike = str(staff_timelike)
        if staff_gender == 0:
            staff_gender = 'male'
        else:
            staff_gender = 'female'

        staff = Staff(name=staff_name, gender=staff_gender, birthyear=staff_birthyear, workyear=staff_workyear,daylike=staff_daylike,timelike=staff_timelike)
        try:
            db.session.add(staff)
            db.session.commit()
            dbstatus.changestatus(True)
            print(dbstatus.isChange)
            # return 'OK'
            return redirect('/schedulesystem/staff/')
        except Exception as e:
            db.session.rollback()
            db.session.flush()
            return 'add staff fail' + str(e)


# 网站信息的接口
@front.route('/schedulesystem/about/', methods=['GET', 'POST'])
def about():
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    return render_template('front/front_about.html', flag=flag, user=user)

# 门店信息界面客流量数据接口
@front.route('/schedulesystem/introduction/graph/', methods=['GET'])
def graph():
    # 从数据库中查询最新的客流量数据
    customer_flow = Customer_flow.query.order_by(Customer_flow.week.desc()).first()
    timelist = ['d1_morning', 'd1_afternoon', 'd1_evening',
                'd2_morning', 'd2_afternoon', 'd2_evening',
                'd3_morning','d3_afternoon', 'd3_evening',
                'd4_morning', 'd4_afternoon', 'd4_evening',
                'd5_morning', 'd5_afternoon','d5_evening',
                'd6_morning', 'd6_afternoon', 'd6_evening',
                'd7_morning', 'd7_afternoon', 'd7_evening']
    list = []

    for i in range(len(timelist)):
        example=getattr(customer_flow,timelist[i])
        list.append(int(example))
    # 返回json数据
    return {'code': 200, 'data_morning': list[0:7],
            'data_afternoon': list[7:14],
            'data_evening': list[14:21]}


# 门店排班信息接口（按周查看）
@front.route('/schedulesystem/schedule/daily/', methods=['GET', 'POST'])
def schedule_daily():
    # 调用算法，生成排班信息
    ans = calculate()
    schedule = transform_day(ans)
    # 将算法生成的排班信息存入数据库
    sche = History(d1_morning=str(schedule['day1time1']), d1_afternoon=str(schedule['day1time2']),d1_evening=str(schedule['day1time3']),
                    d2_morning=str(schedule['day2time1']), d2_afternoon=str(schedule['day2time2']),d2_evening=str(schedule['day2time3']),
                    d3_morning=str(schedule['day3time1']), d3_afternoon=str(schedule['day3time2']),d3_evening=str(schedule['day3time3']),
                    d4_morning=str(schedule['day4time1']), d4_afternoon=str(schedule['day4time2']),d4_evening=str(schedule['day4time3']),
                    d5_morning=str(schedule['day5time1']), d5_afternoon=str(schedule['day5time2']),d5_evening=str(schedule['day5time3']),
                    d6_morning=str(schedule['day6time1']), d6_afternoon=str(schedule['day6time2']),d6_evening=str(schedule['day6time3']),
                    d7_morning=str(schedule['day7time1']), d7_afternoon=str(schedule['day7time2']),d7_evening=str(schedule['day7time3']))
    db.session.add(sche)
    db.session.commit()
    # 从数据库中查询最新的排班信息
    schedule = History.query.order_by(History.time.desc()).first()
    final_schedule = {}
    # 排班数据的字符处理
    for i in range(len(timelist)):
        list = []
        example=getattr(schedule,timelist[i])
        example=example.replace('[','')
        example=example.replace(']','')
        example=example.split(',')
        print(example)
        for j in range(len(example)):
            staff = Staff.query.filter_by(id=int(example[j]) + 1).first()
            list.append(staff.name)
        final_schedule[timelist2[i]] = list
    # 返回排班信息
    dbstatus.changestatus(False)
    return final_schedule

#员工请假审批
@front.route('/schedulesystem/schedule/staff/leave', methods=['GET', 'POST'])
def staff_leave():
    # 判断是否登录
    flag, user_id = if_login()
    # 查询登陆用户信息
    user = User.query.filter_by(id=user_id).first()
    # GET请求，获取员工id，查询员工信息
    if request.method == "GET":
        staff_id = request.args.get('id')
        staff = Staff.query.filter_by(id=staff_id).first()
        print(staff)
        return render_template('front/request/leave_request.html', staff=staff, flag=flag, user=user)
    # POST请求，返回员工信息界面
    else:
        leaveday = request.form.get('day')
        leavetime = request.form.get('time')
        leavestaff = request.form.get('staffid')
        print(leaveday,leavetime,leavestaff)
        if (leaveday == '' or leavetime == '' or leavestaff == ''):
            return redirect('/schedulesystem/staff/request')
        else:
            # print(leaveday,leavetime,leavestaff)
            sch, new_schedule, leave_staff, change_staff, leaveday, leavetime = main(int(leavestaff)-1, int(leaveday)-1, int(leavetime))
            # print(sch)
            # print(new_schedule)
            # print(leave_staff)
            # print(change_staff)
            leave_info = [leave_staff,leaveday,leavetime,2]
            change_info = [change_staff,leaveday,leavetime,3]
            info = [leave_info,change_info]
            schedule = transform_day(new_schedule)
            # 将算法生成的排班信息存入数据库
            sche = History(d1_morning=str(schedule['day1time1']), d1_afternoon=str(schedule['day1time2']),
                           d1_evening=str(schedule['day1time3']),
                           d2_morning=str(schedule['day2time1']), d2_afternoon=str(schedule['day2time2']),
                           d2_evening=str(schedule['day2time3']),
                           d3_morning=str(schedule['day3time1']), d3_afternoon=str(schedule['day3time2']),
                           d3_evening=str(schedule['day3time3']),
                           d4_morning=str(schedule['day4time1']), d4_afternoon=str(schedule['day4time2']),
                           d4_evening=str(schedule['day4time3']),
                           d5_morning=str(schedule['day5time1']), d5_afternoon=str(schedule['day5time2']),
                           d5_evening=str(schedule['day5time3']),
                           d6_morning=str(schedule['day6time1']), d6_afternoon=str(schedule['day6time2']),
                           d6_evening=str(schedule['day6time3']),
                           d7_morning=str(schedule['day7time1']), d7_afternoon=str(schedule['day7time2']),
                           d7_evening=str(schedule['day7time3']),change=str(info))
            db.session.add(sche)
            db.session.commit()
            return  redirect('/schedulesystem/schedulestaff')


