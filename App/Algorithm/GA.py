import numpy as np
import pandas as pd
import random
import math

def readlist(str):
    output=[]
    for i in str:
        if i != ',':
            output.append(int(i))
    return output

def init(sch,num):
    for i in range(len(sch)):
        for j in range(len(sch[i])):
            sch[i][j]=random.sample(range(0,num),len(sch[i][j]))

    return sch

def calfit(sch,list_staffday,list_stafftime):
    fit=0
    for i in range(len(sch)):
        for j in range(len(sch[i])):
            for k in range(len(sch[i][j])):
                if i not in list_staffday[sch[i][j][k]] and j not in list_staffday[sch[i][j][k]]:
                    fit+=3
                elif i not in list_staffday[sch[i][j][k]] or j not in list_staffday[sch[i][j][k]]:
                    fit+=2
                else:
                    fit+=0

    for n in range(len(list_staffday)):
        for i in range(len(sch)):
            continue_time = 0
            for j in range(len(sch[i])):
                if n in sch[i][j]:
                    continue_time+=1
            if continue_time>2:
                fit+=3
            elif continue_time>1:
                fit+=1

    continue_worktime={}

    for n in range(len(list_staffday)):
        continue_worktime[n] = 0
        for i in range(len(sch)):
            for j in range(len(sch[i])):
                if n in sch[i][j]:
                    continue_worktime[n]+=1
    for i in continue_worktime.keys():
        if continue_worktime[i]>10:
            fit+=4
        elif continue_worktime[i]<5:
            fit+=4

    return 1/fit

def swap(sch1,sch2):
    i1 = random.randint(0,6)
    i2 = random.randint(0,6)
    j1 = random.randint(0,2)
    j2 = random.randint(0, 2)
    k1 = random.randint(0,len(sch1[i1][j1])-1)
    k2 = random.randint(0, len(sch2[i2][j2]) - 1)
    while( (sch1[i1][j1][k1] in sch2[i2][j2]) or (sch2[i2][j2][k2] in sch1[i1][j1])):
        i1 = random.randint(0, 6)
        i2 = random.randint(0, 6)
        j1 = random.randint(0, 2)
        j2 = random.randint(0, 2)
        k1 = random.randint(0, len(sch1[i1][j1]) - 1)
        k2 = random.randint(0, len(sch2[i2][j2]) - 1)
    t=sch1[i1][j1][k1]
    sch1[i1][j1][k1]=sch2[i2][j2][k2]
    sch2[i2][j2][k2]=t
    return sch1,sch2

def variation(sch,num_staff):
    i1 = random.randint(0, 6)
    j1 = random.randint(0, 2)
    k1 = random.randint(0, len(sch[i1][j1]) - 1)
    var = random.randint(0, num_staff-1)
    while (var in sch[i1][j1]):
        i1 = random.randint(0, 6)
        j1 = random.randint(0, 2)
        k1 = random.randint(0, len(sch[i1][j1]) - 1)
        var = random.randint(0, num_staff-1)
    sch[i1][j1][k1]=var
    return  sch


df_cus = pd.read_excel('data.xlsx')
df_staff = pd.read_excel('data2.xlsx')

list_num=[]
for i in range(len(df_cus['日期'])):
    if i%3==0:
        num = []
        for j in range(3):
            num.append(int(df_cus['客流量'][i+j]))
        list_num.append(num)
#print(list_num)

list_staffday = []
list_stafftime = []
num_staff=len(df_staff['员工编号'])
for i in range(len(df_staff['员工编号'])):
    list_staffday.append(readlist(str(df_staff['员工天偏好'][i])))
    list_stafftime.append(readlist(str(df_staff['员工时间偏好'][i])))
# print(list_staffday)
# print(list_stafftime)


#生成初始种群
plan_sch=[]
N=20
for i in range(N):
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
    plan_sch.append(init(schdule,num_staff))
# print(plan_sch)

tot_cal=[]
for i in plan_sch:
    tot_cal.append(calfit(i, list_staffday, list_stafftime))

def cal_rate(list_cal):
    rate=[]
    rate_t=[]
    for i in list_cal:
        rate.append(i/sum(list_cal))
    sm=0
    for i in range(len(rate)):
        rate_t.append(rate[i]+sm)
        sm+=rate[i]
    return rate_t

#执行遗传算法
GENERATION=100
rate_pro=0.6

plan=plan_sch.copy()
original=[1/calfit(i, list_staffday, list_stafftime) for i in plan]
print(original)

for i in range(GENERATION):
    plan_choice=[]
    for j in range(int(N/2)):
        choice = []
        if len(plan)>2:
            for k in range(2):
                tot_cal = []
                for i in plan:
                    tot_cal.append(calfit(i, list_staffday, list_stafftime))
                list_rate = cal_rate(tot_cal)
                rate=random.random()
                for q in range(len(list_rate)):
                    if rate<list_rate[q]:
                        choice.append(plan[q])
                        plan.remove(plan[q])
                        break
        else:
            for k in range(2):
                choice.append(plan[k])
            for l in range(2):
                plan.remove(choice[l])
        old1=choice[0]
        old2=choice[1]
        new1,new2=swap(old1,old2)
        rate_v=random.random()
        if rate_v>rate_pro:
            new1 = variation(new1,num_staff)
            new2 = variation(new2, num_staff)
        if calfit(new1, list_staffday, list_stafftime) > calfit(old1, list_staffday, list_stafftime):
            plan_choice.append(new1)
        else:
            plan_choice.append(old1)
        if calfit(new2, list_staffday, list_stafftime) > calfit(old2, list_staffday, list_stafftime):
            plan_choice.append(new2)
        else:
            plan_choice.append(old2)
    plan=plan_choice.copy()

list_ans=[]
for i in plan:
    ans=1/calfit(i, list_staffday, list_stafftime)
    list_ans.append(ans)

print(min(list_ans))



