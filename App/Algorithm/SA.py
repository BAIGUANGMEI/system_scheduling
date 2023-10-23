import pandas as pd
import random
import math
import matplotlib.pyplot as plt


def readlist(str):
    output = []
    for i in str:
        if i != ',':
            output.append(int(i))
    return output


def init(sch, num):
    for i in range(len(sch)):
        for j in range(len(sch[i])):
            sch[i][j] = random.sample(range(0, num), len(sch[i][j]))

    return sch


def calfit(sch, list_staffday, list_stafftime):
    fit = 0
    for i in range(len(sch)):
        for j in range(len(sch[i])):
            for k in range(len(sch[i][j])):
                if i not in list_staffday[sch[i][j][k]] and j not in list_staffday[sch[i][j][k]]:
                    fit += 3
                elif i not in list_staffday[sch[i][j][k]] or j not in list_staffday[sch[i][j][k]]:
                    fit += 2
                else:
                    fit += 0

    for n in range(len(list_staffday)):
        for i in range(len(sch)):
            continue_time = 0
            for j in range(len(sch[i])):
                if n in sch[i][j]:
                    continue_time += 1
            if continue_time > 2:
                fit += 3
            elif continue_time > 1:
                fit += 1

    continue_worktime = {}

    for n in range(len(list_staffday)):
        continue_worktime[n] = 0
        for i in range(len(sch)):
            for j in range(len(sch[i])):
                if n in sch[i][j]:
                    continue_worktime[n] += 1
    for i in continue_worktime.keys():
        if continue_worktime[i] > 10:
            fit += 4
        elif continue_worktime[i] < 5:
            fit += 4

    return fit


def swap(sch):
    i1 = random.randint(0, 6)
    i2 = random.randint(0, 6)
    j1 = random.randint(0, 2)
    j2 = random.randint(0, 2)
    k1 = random.randint(0, len(sch[i1][j1]) - 1)
    k2 = random.randint(0, len(sch[i2][j2]) - 1)

    while ((sch[i1][j1][k1] in sch[i2][j2]) or (sch[i2][j2][k2] in sch[i1][j1])):
        i1 = random.randint(0, 6)
        i2 = random.randint(0, 6)
        j1 = random.randint(0, 2)
        j2 = random.randint(0, 2)
        k1 = random.randint(0, len(sch[i1][j1]) - 1)
        k2 = random.randint(0, len(sch[i2][j2]) - 1)

    t = sch[i1][j1][k1]
    sch[i1][j1][k1] = sch[i2][j2][k2]
    sch[i2][j2][k2] = t

    return sch


# '../Algorithm/data.xlsx'
# '../Algorithm/data2.xlsx'
def calculate(path1, path2):
    df_cus = pd.read_excel(path1)
    df_staff = pd.read_excel(path2)

    list_num = []
    for i in range(len(df_cus['日期'])):
        if i % 3 == 0:
            num = []
            for j in range(3):
                num.append(int(df_cus['客流量'][i + j]))
            list_num.append(num)
    # print(list_num)

    list_staffday = []
    list_stafftime = []
    num_staff = len(df_staff['员工编号'])

    for i in range(len(df_staff['员工编号'])):
        list_staffday.append(readlist(str(df_staff['员工天偏好'][i])))
        list_stafftime.append(readlist(str(df_staff['员工时间偏好'][i])))
    # print(list_staffday)
    # print(list_stafftime)

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
    # print(sch_ini)
    # print(calfit(sch_ini,list_staffday,list_stafftime))

    T = 30
    EPS = 1e-8
    DELTA = 0.99
    L = 50

    result = []

    old = sch_ini.copy()
    # old=[[[6, 4], [1, 6, 0], [1, 4, 5]], [[2, 0], [3, 5], [0, 5, 1]], [[0, 5], [2, 4, 5], [0, 1, 5]], [[1, 6], [5, 2, 0], [5, 3, 1]], [[4, 2], [1, 6, 5], [4, 1, 5, 3]], [[2, 1, 6], [1, 2, 5, 4], [2, 3, 4, 5]], [[6, 4, 1], [0, 2, 1, 3], [2, 6, 0, 4]]]
    old_cal = calfit(old, list_staffday, list_stafftime)

    while T > EPS:
        for i in range(L):
            new = swap(old)
            new_cal = calfit(new, list_staffday, list_stafftime)
            if new_cal < old_cal:
                old = new
                old_cal = calfit(old, list_staffday, list_stafftime)
                mini = old_cal
                ans = old
                result.append(old_cal)
            elif math.exp(-(new_cal - old_cal) / T) > (0.001 * random.randint(0, 1000)):
                old = new
                old_cal = calfit(old, list_staffday, list_stafftime)
                mini = old_cal
                ans = old
                result.append(old_cal)
        T = T * DELTA

    # plt.plot(pd.DataFrame(result).cummin(axis=0))
    # plt.show()

    return (ans)


def transform_day(ans):
    schedule = {}
    for i in range(len(ans)):
        for j in range(len(ans[i])):
            schedule['day' + str(i + 1) + 'time' + str(j + 1)] = ans[i][j]

    return schedule


def transform_staff(ans, staff_num):
    schedule = {}
    for n in range(staff_num):
        pre = []
        for i in range(len(ans)):
            for j in range(len(ans[i])):
                if n in ans[i][j]:
                    pre.append([i, j])
        schedule['staff' + str(n + 1)] = pre

    return schedule


if __name__ == '__main__':
    ans = calculate('../Algorithm/data.xlsx', '../Algorithm/data2.xlsx')
    print(transform_day(ans))
    print(transform_staff(ans, 7))
