import os
import re
import math

reg_feed = r'FEDRAT/(MMPM,)?([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)$'
patternf = re.compile(reg_feed)
reg_value = r'GOTO/([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)$'
patternv = re.compile(reg_value)

reg_NB_value = r'GOTO/([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)$'
pattern_nb = re.compile(reg_NB_value)

#寻找G00
reg_G = r'GOTO/([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)$'
pattern_g = re.compile(reg_G)

count_s = []
feed_std = []
x_value = []
y_value =[]
z_value = []
i_value = []
j_value = []
k_value =[]
cur_speed = []
x_nb_value = []
y_nb_value = []
z_nb_value = []
Deg_value = []
dmp_value = 3600
F_max = 15000
counting_time = 0.0

read_file = open('YGC2C.cls')
allcontent = read_file.readlines()

w_len = len(allcontent)
print('the whole length is :' + str(w_len))

# def returntodeg(count, j_value, k_value):
#     for j in range(0, count):
    
#         if (float(j_value[j]) >=0 and float(k_value[j]) >= 0):
#             deg_A = 180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159
#         if (float(j_value[j]) < 0 and float(k_value[j]) >0):
#             deg_A = 360+(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
#         if (float(j_value[j]) < 0 and float(k_value[j]) < 0):
#             deg_A = 180+(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
#         if (float(j_value[j]) > 0 and float(k_value[j]) < 0):
#             deg_A = 180-(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
#         Deg_value.append(deg_A)






for i in range(w_len):
    start_match = patternf.match(allcontent[i])
    if(start_match):
        count_s.append(i)
        feed_std.append(allcontent[i])
        cur_speed.append(start_match.group(2))
        print('Find the FeedSpeed :' + start_match.group(2))

c_cot = count_s.count
print('the count of count_s is ', count_s.__len__())
#print('the first len match the alldata is: ' + str(count_s[0]))

#在速度参数之前寻找匹配数据值，即为G00语句
for i in range(count_s[0]):
    g_match = pattern_g.match(allcontent[i])
    if(g_match):
        xo = g_match.group(1)
        yo = g_match.group(2)
        zo = g_match.group(3)
        io = g_match.group(4)
        jo = g_match.group(5)
        ko = g_match.group(6)
        #记录G00当前语句的角度值，用于后续计算的初始值使用
        if (float(jo) >=0 and float(ko) >= 0):
            deg_ori = 180*math.atan(float(jo)/float(ko)) / 3.14159
        if (float(jo) < 0 and float(ko) >0):
            deg_ori= 360+(180*math.atan(float(jo)/float(ko)) / 3.14159)
        if (float(jo) < 0 and float(ko) < 0):
            deg_ori = 180+(180*math.atan(float(jo)/float(ko)) / 3.14159)
        if (float(jo) > 0 and float(ko) < 0):
            deg_ori = 180-(180*math.atan(float(jo)/float(ko)) / 3.14159)
print('The first Origin Degree is: ' + str(deg_ori))      


#匹配没有角度的XYZ数值
for i in range(count_s[0], count_s[1]):
    nb_match = pattern_nb.match(allcontent[i])
    if(nb_match):
        x_nb_value.append(nb_match.group(1))
        y_nb_value.append(nb_match.group(2))
        z_nb_value.append(nb_match.group(3))

#验证存储的武角度坐标值
# for nu in range(len(x_nb_value)):
#     print('X NO B value is: ' + str(x_nb_value[nu]))
#     print('Y NO B value is: ' + str(y_nb_value[nu]))
#     print('Z NO B value is: ' + str(z_nb_value[nu]))

for i in range(count_s.__len__()):
    print('the start index is ' + str(count_s[i]))

#将XYZ坐标分别读入到各自列表中，
for i in range(count_s[1]+1, count_s[2]-1):
    value_match = patternv.match(allcontent[i])
    if (value_match):
        x_value.append(value_match.group(1))
        #print('X value is: ' + value_match.group(1))
        y_value.append(value_match.group(2))
        #print('Y value is: ' + value_match.group(2))
        z_value.append(value_match.group(3))
        #print('Z value is: ' + value_match.group(3))
        i_value.append(value_match.group(4))
        #print('I value is: ' + value_match.group(4))
        j_value.append(value_match.group(5))
        #print('J value is: ' + value_match.group(5))
        k_value.append(value_match.group(6))
        #print('K value is: ' + value_match.group(6))


print('x len is ', len(x_value))
print('y len is ', len(y_value))
print('z len is ', len(z_value))
print('the lenth is ', str(count_s[2]-count_s[1]-3))

#进行计算验证G93指令
L_distance = []  #存储每两点之间的距离
new_speed = []  #存储距离除以速度时的时间，反比后验证是否为变化时间
D_distance = [] #两点之间的角度差值，即角度距离列表

#添加角度列表
for j in range(0, (count_s[2]-count_s[1]-2)):

    
        if (float(j_value[j]) >=0 and float(k_value[j]) >= 0):
            deg_A = 180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159
        if (float(j_value[j]) < 0 and float(k_value[j]) >0):
            deg_A = 360+(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
        if (float(j_value[j]) < 0 and float(k_value[j]) < 0):
            deg_A = 180+(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
        if (float(j_value[j]) > 0 and float(k_value[j]) < 0):
            deg_A = 180-(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
        Deg_value.append(deg_A)


for j in range(0, (count_s[2]-count_s[1]-2)):
    if (j == 0):
        x_dis = float(x_value[0]) - float(x_nb_value[len(x_nb_value)-1])
        y_dis = float(y_value[0]) - float(y_nb_value[len(y_nb_value)-1])
        z_dis = float(z_value[0]) - float(z_nb_value[len(z_nb_value)-1])
        # #角度
        # if (float(j_value[j]) >=0 and float(k_value[j]) >= 0):
        #     deg_A = 180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159
        # if (float(j_value[j]) < 0 and float(k_value[j]) >0):
        #     deg_A = 360+(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
        # if (float(j_value[j]) < 0 and float(k_value[j]) < 0):
        #     deg_A = 180+(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
        # if (float(j_value[j]) > 0 and float(k_value[j]) < 0):
        #     deg_A = 180-(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)

        #deg_A = 360+(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
        #print('the Tan value is: ' + str(math.atan(float(j_value[j])/float(k_value[j]))))
        
        l_dis = math.sqrt(x_dis*x_dis + y_dis*y_dis + z_dis*z_dis)
        r_dis = abs(Deg_value[j] - deg_ori)
        d_time = r_dis / dmp_value 
        t_time = l_dis / float(cur_speed[1])
        all_time = d_time + t_time
        l_feed = 1 / t_time
        d_feed = 1 / d_time
        if (l_feed >= d_feed):
            renew_feed = d_feed
            counting_time = counting_time + d_time
        else:
            renew_feed = l_feed
            counting_time = counting_time + t_time
        #renew_feed = 1 / all_time
        
        L_distance.append(l_dis)
        D_distance.append(r_dis)
        new_speed.append(renew_feed)
        
        
    else:
        x_dis = float(x_value[j]) - float(x_value[j-1])
        y_dis = float(y_value[j]) - float(y_value[j-1])
        z_dis = float(z_value[j]) - float(z_value[j-1])
        # #角度
        # if (float(j_value[j]) >=0 and float(k_value[j]) >= 0):
        #     deg_A = 180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159
        # if (float(j_value[j]) < 0 and float(k_value[j]) >0):
        #     deg_A = 360+(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
        # if (float(j_value[j]) < 0 and float(k_value[j]) < 0):
        #     deg_A = 180+(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
        # if (float(j_value[j]) > 0 and float(k_value[j]) < 0):
        #     deg_A = 180-(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
        #deg_A = 360+(180*math.atan(float(j_value[j])/float(k_value[j])) / 3.14159)
        #print('the Tan value is: ' + str(math.atan(float(j_value[j])/float(k_value[j]))))

        l_dis = math.sqrt(x_dis*x_dis + y_dis*y_dis + z_dis*z_dis)
        r_dis = abs(Deg_value[j] - Deg_value[j-1])
        d_time = r_dis / dmp_value
        t_time = l_dis / float(cur_speed[1])
        all_time = d_time + t_time
        l_feed = 1 / t_time
        d_feed = 1 / d_time
        if (l_feed >= d_feed):
            renew_feed = d_feed
            counting_time = counting_time + d_time
        else:
            renew_feed = l_feed
            counting_time = counting_time + t_time
        #renew_feed = 1 / all_time

        L_distance.append(l_dis)
        D_distance.append(r_dis)
        new_speed.append(renew_feed)
        
        move_speed = 1 / t_time
        #print('the counting speed is ', str(move_speed))

new_y = []
new_z = []
#定义坐标变换函数，这里只有这样一个公式，逆时针旋转一个角度（此时在笛卡尔坐标系下得到一个正角度，顺时针旋转一个角度，在笛卡尔坐标系下得到一个负角度，负角度对应后面的sin函数正好抵消掉）
def get_new_coordinate(oy, oz, delta):
    ues_delta = (delta * math.pi) / 180
    ny = oy*math.cos(ues_delta) - oz*math.sin(ues_delta)
    nz = oz*math.cos(ues_delta) + oy*math.sin(ues_delta)
    new_y.append(ny)
    new_z.append(nz)

#get_new_coordinate(-45.3712, -13.5701, 335.323)
print(math.cos(2*math.pi))
#print("计算转换角度值： " + str(math.atan(-0.4174955/0.9086790)))
#print('转换后的坐标为： ' + str(new_y[0]) + " " + str(new_z[0]) + " ")
for m in range(0, (count_s[2]-count_s[1]-2)):
    get_new_coordinate(float(y_value[m]), float(z_value[m]), Deg_value[m])
    

#print('the speed is ' + str(cur_speed[1]))
# for i in range(len(L_distance)):
#     print('every dis is ', L_distance[i])
print('Total Cutting Time is: ' + str(counting_time))
for k in range(len(x_value)):
    print('X: ' + str(x_value[k]) + "  " + 'Y: ' + str(new_y[k]) + " " + 'Z: ' + str(new_z[k]) + " " + 'B: '+ str(Deg_value[k]) + " " + 'speed: ' + str(new_speed[k]))






