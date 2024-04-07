import pandas as pd
import random
import math
import matplotlib.pyplot as plt
import time
import pymysql

# 字符处理方法1
def readlist(str):
    output = []
    if str=='nan':
        return range(0,7)
    for i in str:
        if i != ',':
            output.append(int(i))
    return output

# 字符处理方法2
def readlist_1(str):
    str = str.replace('[','').replace(']','')
    output= str.split(',')
    for i in range(len(output)):
        output[i]=int(output[i])
    return output

# 初始化数据
def init(sch, num):
    for i in range(len(sch)):
        for j in range(len(sch[i])):
            sch[i][j] = random.sample(range(0, num), len(sch[i][j]))

    return sch

# 计算适应度
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

# 复制列表
def copy_list(sch):
    s_sch = []
    for i in range(len(sch)):
        day=[]
        for j in range(len(sch[i])):
            time=sch[i][j].copy()
            day.append(time)
        s_sch.append(day)
    return s_sch

# 随机交换
def swap(sch):
    original = copy_list(sch)
    i1 = random.randint(0, 6)
    i2 = random.randint(0, 6)
    j1 = random.randint(0, 2)
    j2 = random.randint(0, 2)
    k1 = random.randint(0, len(original[i1][j1]) - 1)
    k2 = random.randint(0, len(original[i2][j2]) - 1)

    while ((original[i1][j1][k1] in original[i2][j2]) or (original[i2][j2][k2] in original[i1][j1])):
        i1 = random.randint(0, 6)
        i2 = random.randint(0, 6)
        j1 = random.randint(0, 2)
        j2 = random.randint(0, 2)
        k1 = random.randint(0, len(original[i1][j1]) - 1)
        k2 = random.randint(0, len(original[i2][j2]) - 1)

    t = original[i1][j1][k1]
    original[i1][j1][k1] = original[i2][j2][k2]
    original[i2][j2][k2] = t

    return original

# 随机变换
def change(sch,staff_num):
    original = copy_list(sch)
    i = random.randint(0, 6)
    j = random.randint(0, 2)
    t = random.randint(0, staff_num-1)
    while t in original[i][j]:
        t = random.randint(0, staff_num - 1)
    k = random.randint(0, len(original[i][j]) - 1)
    original[i][j][k] = t
    return original

# 连接数据库
def connect_db():
    db = pymysql.connect(host='124.220.80.142',
                         user='root',
                         password='mzh553214',
                         database='systemdb',
                         charset='utf8')
    return db

# 获取员工数据
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

        cursor.close()

        return data_day,data_time,num_staff

    except:
        print("get data false")

# 获取客流数据
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

# 算法部分
def calculate():

    # 连接数据库
    db = connect_db()
    print("connect success!")
    list_staffday,list_stafftime,num_staff=get_data(db)

    customer_num=get_customer_flow(db)
    db.close()

    # 初始化排班
    list_num = []
    for i in range(0, len(customer_num)):
        if i % 3 == 0:
            num = []
            for j in range(3):
                num.append(customer_num[i + j])
            list_num.append(num)

    schdule = [[] for i in range(len(list_num))]

    for i in range(len(list_num)):
        for j in range(len(list_num[i])):
            k = list_num[i][j]
            if k >= 200:
                schdule[i].append([0 for i in range(4)])
            elif k > 100 and k < 200:
                schdule[i].append([0 for i in range(3)])
            else:
                schdule[i].append([0 for i in range(2)])

    sch_ini = init(schdule, num_staff)

    T = 30
    EPS = 1e-8
    DELTA = 0.99
    L = 50

    result = []
    result_s=[]

    #模拟退火算法
    old = copy_list(sch_ini)
    old_cal = calfit(old, list_staffday,list_stafftime, num_staff)

    while T > EPS:
        for i in range(L):
            new = change(old,num_staff)
            new_cal = calfit(new, list_staffday,list_stafftime, num_staff)
            if new_cal < old_cal:
                result.append(calfit(new, list_staffday,list_stafftime, num_staff))
                result_s.append(new)
                old = copy_list(new)
                old_cal = new_cal
            elif math.exp(-(new_cal - old_cal) / T) > (0.001 * random.randint(0, 1000)):
                result.append(calfit(new, list_staffday,list_stafftime, num_staff))
                result_s.append(new)
                old = copy_list(new)
                old_cal = new_cal

        T = T * DELTA

    # plt.plot(pd.DataFrame(result).cummin(axis=0))
    # plt.plot(pd.DataFrame(result))
    # plt.show()
    # print(min(result))
    # print(calfit(result_s[result.index(min(result))], list_staffday,list_stafftime, num_staff))
    # print(result_s)
    return result_s[result.index(min(result))]

# 按天查看排班转换
def transform_day(ans):
    schedule = {}
    for i in range(len(ans)):
        for j in range(len(ans[i])):
            schedule['day' + str(i + 1) + 'time' + str(j + 1)] = ans[i][j]

    return schedule

# 按员工查看排班转换
def transform_staff(ans, num_staff):
    schedule = {}
    for n in range(num_staff):
        pre = []
        for i in range(len(ans)):
            for j in range(len(ans[i])):
                if n in ans[i][j]:
                    pre.append([i, j])
        schedule['staff' + str(n + 1)] = pre

    return schedule

if __name__ == '__main__':
    start = time.time()
    ans = calculate()
    print(ans)
    print(transform_day(ans))
    print(transform_staff(ans, 8))
    # db = connect_db()
    # print(get_customer_flow(db))
    end = time.time()
    print('Running time: %s Seconds' % (end - start))

