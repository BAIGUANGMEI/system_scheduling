import random

def change(sch):
    i= random.randint(0, 1)
    j = random.randint(0, 1)
    k = random.randint(0, len(sch[i][j]) - 1)
    t = random.randint(0, 10)
    sch[i][j][k] = t
    return sch

def copy_list(sch):
    s_sch = []
    for i in range(len(sch)):
        day=[]
        for j in range(len(sch[i])):
            time=[]
            for k in range(len(sch[i][j])):
                time.append(sch[i][j][k])
            day.append(time)
        s_sch.append(day)
    return s_sch
a=[[[1,2,3],[4,5,6]],[[7,8,9],[10,11,12]]]
s_a=copy_list(a)
print(s_a)
a[0][0][0]=0
print(a)
print(s_a)
