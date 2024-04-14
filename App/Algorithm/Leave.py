import random
import math
import pymysql

def connect_db():
    db = pymysql.connect(host='124.220.80.142',
                         user='root',
                         password='mzh553214',
                         database='systemdb',
                         charset='utf8')
    return db

def readlist_1(str):
    str = str.replace('[','').replace(']','')
    output= str.split(',')
    for i in range(len(output)):
        output[i]=int(output[i])
    return output

def get_customer_flow(db):
    cursor = db.cursor()

    try:
        sql = "select * from customer_flow where week=1"

        cursor.execute(sql)
        result = cursor.fetchall()
        customer_flow=[]
        for data in range(1,len(result[0])-1):
            customer_flow.append(result[0][data])

        cursor.close()

        print("get customer flow victory!")
        return customer_flow

    except:
        print("get customer flow false")

def get_data(db):
    cursor = db.cursor()
    try:
        sql = "select * from staff"

        cursor.execute(sql)

        result = cursor.fetchall()
        data_day=[]
        data_time=[]
        for data in result:
            # print(data)
            if data[5]!=None and data[6]!=None:
                data_day.append(readlist_1(data[5]))
                data_time.append(readlist_1(data[6]))
            elif data[5]==None and data[6]!=None:
                data_day.append([i for i in range(0,7)])
                data_time.append(readlist_1(data[6]))
            elif data[5]!=None and data[6]==None:
                data_day.append(readlist_1(data[5]))
                data_time.append([i for i in range(0,7)])
            else:
                data_day.append([i for i in range(0,7)])
                data_time.append([i for i in range(0,7)])
        num_staff=len(result)
        print("get data victory!")

        cursor.execute("select id from staff")
        id_list = cursor.fetchall()
        id_list = [i[0] for i in id_list]

        cursor.close()

        return data_day,data_time,num_staff,id_list

    except:
        print("get data false")

# 计算员工的满意度
def calfit(sch, list_staffday,list_stafftime ,num_staff):

    # 工作日偏好及工作时间偏好
    fit = 0
    for i in range(len(sch)):
        for j in range(len(sch[i])):
            for k in range(len(sch[i][j])):
                if i not in list_staffday[sch[i][j][k]] and j not in list_stafftime[sch[i][j][k]]:
                    fit += 2
                elif i not in list_staffday[sch[i][j][k]] or j not in list_stafftime[sch[i][j][k]]:
                    fit += 1
                else:
                    fit += 0

    # 一天内工作班次
    for n in range(0,num_staff):
        for i in range(len(sch)):
            continue_time = 0
            for j in range(len(sch[i])):
                if n in sch[i][j]:
                    continue_time += 1
            if continue_time > 2:
                fit += 2
            elif continue_time > 1:
                fit += 1

    # 连续工作班次
    continue_worktime = {}

    for n in range(0,num_staff):
        continue_worktime[n] = 0
        for i in range(len(sch)):
            for j in range(len(sch[i])):
                if n in sch[i][j]:
                    continue_worktime[n] += 1
    for i in continue_worktime.keys():
        if continue_worktime[i] > 10 or continue_worktime[i] < 6:
            fit += 100

    return fit

def copy_list(sch):
    s_sch = []
    for i in range(len(sch)):
        day=[]
        for j in range(len(sch[i])):
            time=sch[i][j].copy()
            day.append(time)
        s_sch.append(day)
    return s_sch

# 转化为原本的排班列表
def trans2sch(sch):
    schedule = [[] for i in range(7)]
    for i in range(len(sch)):
        if i % 3 == 0:
            schedule[i // 3].append(sch[i])
            schedule[i // 3].append(sch[i + 1])
            schedule[i // 3].append(sch[i + 2])
    return schedule

def changeid(sch,id_list):
    for i in sch:
        for j in i:
            for k in range(len(j)):
                j[k] = id_list[j[k]]-1
    return sch

def main(leavestaff,leaveday,leavetime):
    db = connect_db()
    cursor = db.cursor()

    # 获取最新的排班表
    cursor.execute('select * from history where id = (select max(id) from history)')
    result = cursor.fetchall()
    old_schedule = list(result[0][1:22])

    list_staffday, list_stafftime, num_staff, id_list = get_data(db)

    # 将字符串转换为列表
    for i in range(len(old_schedule)):
        old_schedule[i] = old_schedule[i].strip('[]')
        old_schedule[i] = old_schedule[i].split(',')
        for j in range(len(old_schedule[i])):
            old_schedule[i][j] = int(old_schedule[i][j])
    # print(trans2sch(old_schedule))
    old_schedule = trans2sch(old_schedule)
    for i in old_schedule:
        for j in i:
            for k in range(len(j)):
                j[k] = id_list.index(j[k]+1)
    # print(old_schedule)

    # print(calfit(trans2sch(old_schedule), list_staffday, list_stafftime, num_staff))
    # print(calfit_change(trans2sch(old_schedule), list_staffday, list_stafftime, num_staff,leavestaff,leaveday,leavetime))
    sch = old_schedule

    minimum = 1000000

    for i in id_list:
        if i-1 != leavestaff and i-1 not in sch[leaveday][leavetime]:
            new_sch = copy_list(sch)
            new_sch[leaveday][leavetime].remove(id_list.index(leavestaff+1))
            new_sch[leaveday][leavetime].append(id_list.index(i))
            if calfit(new_sch, list_staffday, list_stafftime, num_staff) < minimum:
                minimum = calfit(new_sch, list_staffday, list_stafftime, num_staff)
                new_schedule = copy_list(new_sch)
                # print(minimum)
    # print(new_schedule)
    db.close()

    sch = changeid(sch,id_list)
    new_schedule = changeid(new_schedule,id_list)

    leave_staff = sch[leaveday][leavetime][sch[leaveday][leavetime].index(leavestaff)]

    change_staff = new_schedule[leaveday][leavetime][sch[leaveday][leavetime].index(leavestaff)]


    return sch,new_schedule,leave_staff,change_staff,leaveday,leavetime

if __name__ == '__main__':
    sch,new_schedule,leave_staff,change_staff,leaveday,leavetime = main(12,0,1)
    print(sch)
    print(new_schedule)
    print(leave_staff)
    print(change_staff)