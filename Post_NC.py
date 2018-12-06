## -*- coding: utf-8 -*-

import os
import re
import math

from tkinter import *
import tkinter.filedialog

import numpy as np


'''
要提取的参数信息：
刀具长度，切削刃长度，刀具名称，当前程序名称
通过正则表达式读取对应信息
识别G0
识别FEDRAT
识别G1
识别并去除重复坐标值
识别G2,G3

'''
#定义G0匹配字符串
reg_G0_head = r'RAPID\n'
reg_G0_match = r'GOTO/([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)(?:,([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\n|\n)'
#reg_G0_match = r'GOTO/([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)|GOTO/([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
#定义普通G1匹配字符串
reg_G1 = r'GOTO/([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)(?:,([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\n|\n)'
reg_G2_G3 = r'CIRCLE/([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_G23_nextline = r'GOTO/([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_pre_line = r'(?:G00|G01|G02|G03)\sX([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\sY([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\sZ([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)(.*)'

#reg_G3_newout = r'(G00|G01|G02|G03)\s(X[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Y[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Z[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(F[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
#上面的正则表达式，G02,G03无法匹配，原因是后面灭有对应的I，J，K选项，加上这三个匹配项，但是，前面加"?"表示为可选，有的时候就是G02，G03，没有的时候就是G00，G01,且I，J，K三项前面加“？：”定义为非捕捉，既只确定有这一项，但是不匹配值
#reg_G3_newout = r'(G00|G01|G02|G03)\s(X[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Y[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Z[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s?(?:I[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s?(?:J[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s?(?:K[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(F[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_G3_newout_head = r'(G00|G01|G02|G03) .*'
reg_G3_newout_line = r'(G00|G01|G02|G03)\s(X[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Y[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Z[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(F[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_G3_newout_circle_17 = r'(G02|G03)\s(X[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Y[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Z[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(?:I[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)?\s(?:J[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)?\s(F[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_G3_newout_circle_18 = r'(G02|G03)\s(X[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Y[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Z[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(?:I[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)?\s(?:K[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)?\s(F[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_G3_newout_circle_19 = r'(G02|G03)\s(X[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Y[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(Z[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)\s(?:J[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)?\s(?:K[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)?\s(F[+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'   
                                                                                                                                        
#定义速度匹配
#reg_Feed_match = r'FEDRAT/(?:MMPM,|'')([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_Feed_match = r'FEDRAT/(MMPM,)?([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_Spindl_match = r'SPINDL/RPM,([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),CLW'

#定义文件头信息匹配

reg_program_match = r'OPER_NAME_ZCW/(\w+)'
reg_toolname_match = r'TOOL_NAME_ZCW/(\w+)'
#三个参数分别为：下直径，长度，锥度
reg_holder_param = r'HOLDER_PARAM_ZCW/([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
#四个参数分别为：长度，刃长，直径，下半径
reg_tool_param = r'TOOL_PARAM_ZCW/([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_tool_path_length = r'ToolPathLength_ZCW/([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'  #单位时mm
reg_tool_path_cut_length = r'ToolPathCuttingLength_ZCW/([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_tool_path_time = r'ToolPathTime_ZCW/([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'      #单位时分钟，转出时进行时间格式处理
reg_tool_path_cut_time = r'ToolPathCuttingTime_ZCW/([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
#刀具参数信息为：直径，下班经，长度，锥角，尖角，
#*******************************************************
#这两个信息是从原生的NX的clsf文件导出的cls文件带的相关信息，因此单独列出来，添加注释，当使用原生cls文件时，这两个注释信息会起作用
reg_tldata_info = r'TLDATA/MILL,([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),([0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),(?:[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+),(?:[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
reg_toolpath_info = r'TOOL PATH/(\w+),TOOL,(\w+)'
#*******************************************************
reg_load_tool = r'LOAD/TOOL,([0-9]+\.?[0-9]*)'
reg_select_tool = r'SELECT/TOOL,([0-9]+\.?[0-9]*)'
reg_rapid_end = r'RAPID'

#匹配4轴原始数据
reg_4ax_G0_data = r'G00 X([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) Y([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) Z([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) (?:A|B)([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)' #G00 不添加进给速度参数
reg_4ax_G1_data = r'G00 X([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) Y([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) Z([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) (?:A|B)([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) F([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'
#匹配4轴原始数据
reg_4ax_old_data =r'(G00|G01) X([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) Y([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) Z([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) (\w+)([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+) F([+-]?[0-9]+\.?[0-9]*|[0-9]*\.?[0-9]+)'


pattern_G0 = re.compile(reg_G0_head)
pattern_G0_body = re.compile(reg_G0_match)
pattern_G1 = re.compile(reg_G1)
pattern_Feed = re.compile(reg_Feed_match)
pattern_Spindl = re.compile(reg_Spindl_match)
pattern_G2_G3 = re.compile(reg_G2_G3)
pattern_G23_nextline = re.compile(reg_G23_nextline)
pattern_pre = re.compile(reg_pre_line)

pattern_G3_new_output_head = re.compile(reg_G3_newout_head)
pattern_G3_new_output_line = re.compile(reg_G3_newout_line)
pattern_G3_new_output_circle_G17 = re.compile(reg_G3_newout_circle_17)
pattern_G3_new_output_circle_G18 = re.compile(reg_G3_newout_circle_18)
pattern_G3_new_output_circle_G19 = re.compile(reg_G3_newout_circle_19)

#匹配头部信息
pattern_head_programname = re.compile(reg_program_match)
pattern_head_toolnmae = re.compile(reg_toolname_match)
pattern_head_holderparam = re.compile(reg_holder_param)
pattern_head_toolparam = re.compile(reg_tool_param)
pattern_head_path_length = re.compile(reg_tool_path_length)
pattern_head_cut_length = re.compile(reg_tool_path_cut_length)
pattern_head_path_time = re.compile(reg_tool_path_time)
pattern_head_cut_time = re.compile(reg_tool_path_cut_time)
pattern_head_load_tool = re.compile(reg_load_tool)
pattern_head_select_tool = re.compile(reg_select_tool)
pattern_head_rapid_end = re.compile(reg_rapid_end)
#匹配原生的cls信息
pattern_tldata_info = re.compile(reg_tldata_info)
pattern_toolpath_info = re.compile(reg_toolpath_info)

#匹配原始4轴数据，并进行数据更新
pattern_G4_new_G0 = re.compile(reg_4ax_G0_data)
pattern_G4_new_G1 = re.compile(reg_4ax_G1_data)
pattern_G4_oldline = re.compile(reg_4ax_old_data)



G_x0_value = []
G_y0_value = []
G_z0_value = []
G_i0_value = []
G_j0_value = []
G_k0_value = []
G_f0_value = []

G_x_value = []
G_y_value = []
G_z_value = []
G_i_value = []
G_j_value = []
G_k_value = []
G_f_value = []

G_cx_value = []
G_cy_value = []
G_cz_value = []
G_I_value = []
G_J_value = []
G_K_value = []
G_R_value = []

#4 axis degree
G_4ax_degree = []

G_speed = 0.0
G_4_Axis = ''
G_spindl = []
deg_count = 0.0
dmp_value = 3600.0
feed_max = 15000.0
counting_time = 0.0
rv1 = 0.0
rv2 = 0.0
renew_feed = 0.0
forward_roatate = 0
opposite_rotate = 0
axis_4_append_text = ''
axis_5_append_text = ''

#定义要输出的最终G-code代码
G3_code = []
G4_code = []
G5_code = []

G3_new_code = []
G4_new_code = []
G5_new_code = []

#allcontent = []

def readWholeFile_3axis(filename):
    try:
        read_file = open(filename, 'r')
        allcontent = read_file.readlines()
        #contentest = read_file.read()
        #get_match = re.findall(reg_G0, contentest, flags=re.MULTILINE)
        w_len = len(allcontent)
        Gcode_head_3axis(w_len, allcontent, filename)   #单独的读取头部文件信息需要的内容
        match_Feature_line_3axis(w_len, allcontent)
        
        print('The whole 3 Axis length is ' + str(w_len) + '!......')
    

    
    finally:
        read_file.close()

def readWholeFile_4axis(filename):
    try:
        read_file = open(filename, 'r')
        allcontent = read_file.readlines()
        #contentest = read_file.read()
        #get_match = re.findall(reg_G0, contentest, flags=re.MULTILINE)
        w_len = len(allcontent)
        Gcode_head_4axis(w_len, allcontent, filename)
        match_Feature_line_4axis(w_len, allcontent)
        
        print('The whole 4 Axis length is ' + str(w_len) + '!......')
    finally:
        read_file.close()

def readWholeFile_5axis(filename):
    try:
        read_file = open(filename, 'r')
        allcontent = read_file.readlines()
        #contentest = read_file.read()
        #get_match = re.findall(reg_G0, contentest, flags=re.MULTILINE)
        w_len = len(allcontent)
        match_Feature_line_5axis(w_len, allcontent)
        
        print('The whole length is ' + str(w_len) + '!......')
    finally:
        read_file.close()

#匹配3轴后处理
def match_Feature_line_3axis(wlen, alldata):
    
    #print('the translate length is ' + str(wlen))
    cnum = 0
    while cnum < wlen:                              #for i in range(wlen):
        
        get_G0_match = pattern_G0.match(alldata[cnum])
        get_G1_match = pattern_G1.match(alldata[cnum])
        get_Feed_match = pattern_Feed.match(alldata[cnum])
        get_Spindl_match = pattern_Spindl.match(alldata[cnum])
        get_G23_match = pattern_G2_G3.match(alldata[cnum])
        global G_speed
        #print(len(get_G0_match))
        # for j in range(len(get_G0_match)):
        #     print(get_G0_match[j])
        #print('the each line is ' + str(alldata[i]))
        if (get_Spindl_match):
            #print('The spindl speed is: ' + get_Spindl_match.group(1))
            G_spindl.append(get_Spindl_match.group(1))
            #print('the count of G_sindl is: ' + str(len(G_spindl)))

        if(get_Feed_match):
            #print('the matche Cutting speed is: ' + get_Feed_match.group(2))
            #G_speed.append(get_Feed_match.group(1))
            G_speed = float(get_Feed_match.group(2))
            #G_speed = gspeed

        if (get_G0_match):
            get_G0_body = pattern_G0_body.search(alldata[cnum+1])
            #print('the next line match is : ' + str(alldata[i+1]))
            if(get_G0_body):
                #print('got match it')
                G_x0_value.append(get_G0_body.group(1))
                G_y0_value.append(get_G0_body.group(2))
                G_z0_value.append(get_G0_body.group(3))
                G_i0_value.append(get_G0_body.group(4))
                G_j0_value.append(get_G0_body.group(5))
                G_k0_value.append(get_G0_body.group(6))
                cnum = cnum + 2
                Gcode_3_style('G00', get_G0_body.group(1), get_G0_body.group(2), get_G0_body.group(3), G_speed)
                continue
                #print('G0' + get_G0_body.group(1) + get_G0_body.group(2) + get_G0_body.group(3) + 'B' + '30' + str(G_speed))
        if(get_G1_match):
            G_x_value.append(get_G1_match.group(1))
            G_y_value.append(get_G1_match.group(2))
            G_z_value.append(get_G1_match.group(3))
            G_i_value.append(get_G1_match.group(4))
            G_j_value.append(get_G1_match.group(5))
            G_k_value.append(get_G1_match.group(6))
            Gcode_3_style('G01', get_G1_match.group(1), get_G1_match.group(2), get_G1_match.group(3), G_speed)

        if(get_G23_match):
            pass
            #存圆心坐标，通过判断圆弧在哪个平面来判断用哪两个坐标系
            w_plane = ''
            cxx = 0.0
            cyy = 0.0
            czz = 0.0
            wp1 = int(float(get_G23_match.group(4)))
            wp2 = int(float(get_G23_match.group(5)))
            wp3 = int(float(get_G23_match.group(6)))
            get_G23_nextline_match = pattern_G23_nextline.match(alldata[cnum+1])
            if(get_G23_nextline_match):
                ex = float(get_G23_nextline_match.group(1))
                ey = float(get_G23_nextline_match.group(2))
                ez = float(get_G23_nextline_match.group(3))

            #l_len = len(G3_code)
            #print('the length of G3 code is: ' + str(l_len))
            get_pre_match = pattern_pre.match(G3_code[len(G3_code) - 1])
            if(get_pre_match):
                px = float(get_pre_match.group(1))
                py = float(get_pre_match.group(2))
                pz = float(get_pre_match.group(3))

                cx = float(get_G23_match.group(1))
                cy = float(get_G23_match.group(2))
                cz = float(get_G23_match.group(3))

                cxx = cx - px
                cyy = cy - py
                czz = cz - pz
            
            if(wp1 == 1):
                w_plane = 'G19'
    
                Gcode_3_circle_style('G02', 'G19', ex, ey, ez, cxx, cyy, czz, G_speed)

            if(wp1 == -1):
                w_plane = 'G19'

                Gcode_3_circle_style('G03', 'G19', ex, ey, ez, cxx, cyy, czz, G_speed)

            if(wp2 == 1):
                w_plane = 'G18'

                Gcode_3_circle_style('G02', 'G18', ex, ey, ez, cxx, cyy, czz, G_speed)

            if(wp2 == -1):
                w_plane = 'G18'

                Gcode_3_circle_style('G03', 'G18', ex, ey, ez, cxx, cyy, czz, G_speed)

            if(wp3 == 1):
                w_plane = 'G17'

                Gcode_3_circle_style('G02', 'G17', ex, ey, ez, cxx, cyy, czz, G_speed)

            if(wp3 == -1):
                w_plane = 'G17'

                Gcode_3_circle_style('G03', 'G17', ex, ey, ez, cxx, cyy, czz, G_speed)


            cnum = cnum + 2
            continue
        cnum = cnum + 1

        #refresh_file(G3_code)

            
            #print('We got the match!......')
    # for j in range(len(G_x0_value)):
    #     print('X: ' + str(G_x0_value[j]) + ' Y：' + str(G_y0_value[j]) + ' Z: ' + str(G_z0_value[j]) + ' I: ' + str(G_i0_value[j]) + ' J: ' + str(G_j0_value[j]) + ' K: ' + str(G_k0_value[j]))
    
    

#匹配4轴后处理
def match_Feature_line_4axis(wlen, alldata):
    cnum =0 
    while cnum < wlen:
        get_G0_match = pattern_G0.match(alldata[cnum])
        get_G1_match = pattern_G1.match(alldata[cnum])
        get_Feed_match = pattern_Feed.match(alldata[cnum])
        get_Spindl_match = pattern_Spindl.match(alldata[cnum])

        global G_speed  #返回当前速度值
        global G_4_Axis #返回当前旋转轴标识
        global deg_count #此数据用于计算反正切值，并传递该值进行坐标变化计算使用

        if (get_Spindl_match):
            #print('The spindl speed is: ' + get_Spindl_match.group(1))
            G_spindl.append(get_Spindl_match.group(1))
            #print('the count of G_sindl is: ' + str(len(G_spindl)))

        if(get_Feed_match):
            #print('the matche Cutting speed is: ' + get_Feed_match.group(2))
            #G_speed.append(get_Feed_match.group(1))
            G_speed = float(get_Feed_match.group(2))
            #G_speed = gspeed

        if (get_G0_match):
            get_G0_body = pattern_G0_body.search(alldata[cnum+1])
            #print('the next line match is : ' + str(alldata[i+1]))
            if(get_G0_body):
                #print('got match it')
                G_x0_value.append(get_G0_body.group(1))
                G_y0_value.append(get_G0_body.group(2))
                G_z0_value.append(get_G0_body.group(3))
                G_i0_value.append(get_G0_body.group(4))
                G_j0_value.append(get_G0_body.group(5))
                G_k0_value.append(get_G0_body.group(6))
                cnum = cnum + 2
                #Gcode_4_style(head_line, x, y, z, axis_style, ang1, F)
                #角度计算包括主轴正转角度值，反转角度，传递一个参数，记录正转，反转的状态,#hao
                lx = float(get_G0_body.group(1))
                ly = float(get_G0_body.group(2))
                lz = float(get_G0_body.group(3))
                # li = float(get_G0_body.group(4))
                # lj = float(get_G0_body.group(5))
                # lk = float(get_G0_body.group(6))

                if(get_G0_body.group(4) != None):
                    if(float(get_G0_body.group(4)) == 0.0):
                        if(axis_4_append_text == ''):
                            axis_style = 'A'
                        if(axis_4_append_text != ''):
                            axis_style = axis_4_append_text
                        
                        lj = float(get_G0_body.group(5))
                        lk = float(get_G0_body.group(6))

                        if (float(get_G0_body.group(5)) >=0 and float(get_G0_body.group(6)) >= 0):
                            if(forward_roatate == 1):
                                deg_ori = 360-(180*math.atan2(lj,lk) / math.pi)   #正转角度
                            if(opposite_rotate == 1):
                                deg_ori = 360-(360-(180*math.atan2(lj,lk) / math.pi))   #反转角度
                            else:
                                deg_ori = 360-(180*math.atan2(lj,lk) / math.pi)   #正转角度
                        if (float(get_G0_body.group(5)) < 0 and float(get_G0_body.group(6)) >0):
                            if(forward_roatate == 1):
                                deg_ori= -180*math.atan2(lj,lk) / math.pi   #正转角度
                            if(opposite_rotate == 1):
                                deg_ori= 360-(-180*math.atan2(lj,lk) / math.pi)   #反转角度
                            else:
                                deg_ori= -180*math.atan2(lj,lk) / math.pi   #正转角度
                        if (float(get_G0_body.group(5)) < 0 and float(get_G0_body.group(6)) < 0):
                            if(forward_roatate == 1):
                                deg_ori = -(180*math.atan2(lj,lk) / math.pi)   #正转角度
                            if(opposite_rotate == 1):
                                deg_ori = 360-(-(180*math.atan2(lj,lk) / math.pi))   #反转角度
                            else:
                                deg_ori = -(180*math.atan2(lj,lk) / math.pi)   #正转角度
                        if (float(get_G0_body.group(5)) > 0 and float(get_G0_body.group(6)) < 0):
                            if(forward_roatate == 1):
                                deg_ori = 360-(180*math.atan2(lj,lk) / math.pi)  #正转角度
                            if(opposite_rotate == 1):
                                deg_ori = 360-(360-(180*math.atan2(lj,lk) / math.pi))  #反转角度
                            else:
                                deg_ori = 360-(180*math.atan2(lj,lk) / math.pi)  #正转角度
                        G_4ax_degree.append(deg_ori)
                        deg_count = math.atan2(lj,lk)
                        get_coordinage_change(ly, lz, deg_count)
                        G_4_Axis = axis_style
                        #Gcode_4_style('G00', get_G0_body.group(1), get_G0_body.group(2), get_G0_body.group(3), axis_style, deg_ori, G_speed)
                        Gcode_4_style('G00', lx, rv1, rv2, axis_style, deg_ori, G_speed)

                    if(float(get_G0_body.group(5)) == 0.0):
                        if(axis_4_append_text == ''):
                            axis_style = 'B'
                        if(axis_4_append_text != ''):
                            axis_style = axis_4_append_text
                        
                        li = float(get_G0_body.group(4))
                        lk = float(get_G0_body.group(6))

                        if (float(get_G0_body.group(4)) >=0 and float(get_G0_body.group(6)) >= 0):
                            if(forward_roatate == 1):
                                deg_ori = 180*math.atan2(li,lk) / math.pi        #正转角度
                            if(opposite_rotate == 1):
                                deg_ori = 360-(180*math.atan2(li,lk) / math.pi)   #反转角度
                            else:
                                deg_ori = 180*math.atan2(li,lk) / math.pi        #正转角度
                        if (float(get_G0_body.group(4)) < 0 and float(get_G0_body.group(6)) >0):
                            if(forward_roatate == 1):
                                deg_ori= 360+180*math.atan2(lj,lk) / math.pi        #正转角度
                            if(opposite_rotate == 1):
                                deg_ori= 360-(360+180*math.atan2(lj,lk) / math.pi)   #反转角度
                            else:
                                deg_ori= 360+180*math.atan2(lj,lk) / math.pi        #正转角度
                        if (float(get_G0_body.group(4)) < 0 and float(get_G0_body.group(6)) < 0):
                            if(forward_roatate == 1):
                                deg_ori= 360+180*math.atan2(lj,lk) / math.pi        #正转角度
                            if(opposite_rotate == 1):
                                deg_ori= 360-(360+180*math.atan2(lj,lk) / math.pi)   #反转角度
                            else:
                                deg_ori= 360+180*math.atan2(lj,lk) / math.pi        #正转角度
                        if (float(get_G0_body.group(4)) > 0 and float(get_G0_body.group(6)) < 0):
                            if(forward_roatate == 1):
                                deg_ori = 180*math.atan2(lj,lk) / math.pi       #正转角度
                            if(opposite_rotate == 1):
                                deg_ori = 360-(180*math.atan2(lj,lk) / math.pi)  #反转角度
                            else:
                                deg_ori = 180*math.atan2(lj,lk) / math.pi       #正转角度
                        G_4ax_degree.append(deg_ori)
                        get_coordinage_change(li, lk, deg_ori)
                        G_4_Axis = axis_style
                        #Gcode_4_style('G00', get_G0_body.group(1), get_G0_body.group(2), get_G0_body.group(3), axis_style, deg_ori, G_speed)
                        Gcode_4_style('G00', rv1, ly, rv2, axis_style, deg_ori, G_speed)

                else:
                    if(G_4_Axis == 'A'):
                        # lj = float(get_G0_body.group(5))
                        # lk = float(get_G0_body.group(6))
                        # deg_count = math.atan2(lj,lk)
                        get_coordinage_change(ly, lz, deg_count)
                        Gcode_4_style('G00', lx, rv1, rv2, G_4_Axis, G_4ax_degree[len(G_4ax_degree)-1], G_speed)
                    if(G_4_Axis == 'B'):
                        # li = float(get_G0_body.group(4))
                        # lk = float(get_G0_body.group(6))
                        # deg_count = math.atan2(li,lk)
                        get_coordinage_change(lx, lz, deg_count)
                        Gcode_4_style('G00', rv1, ly, rv2, G_4_Axis, G_4ax_degree[len(G_4ax_degree)-1], G_speed)
                continue


        if(get_G1_match):
            G_x_value.append(get_G1_match.group(1))
            G_y_value.append(get_G1_match.group(2))
            G_z_value.append(get_G1_match.group(3))
            G_i_value.append(get_G1_match.group(4))
            G_j_value.append(get_G1_match.group(5))
            G_k_value.append(get_G1_match.group(6))

            #用于换算坐标系
            lx = float(get_G1_match.group(1))
            ly = float(get_G1_match.group(2))
            lz = float(get_G1_match.group(3))
            # li = float(get_G1_match.group(4))
            # lj = float(get_G1_match.group(5))
            # lk = float(get_G1_match.group(6))

            if(get_G1_match.group(4) != None):
                if(float(get_G1_match.group(4)) == 0.0):
                    if(axis_4_append_text == ''):
                        axis_style = 'A'
                    if(axis_4_append_text != ''):
                        axis_style = axis_4_append_text
                    lj = float(get_G1_match.group(5))
                    lk = float(get_G1_match.group(6))

                    if (float(get_G1_match.group(5)) >=0 and float(get_G1_match.group(6)) >= 0):
                        if(forward_roatate == 1):
                            deg_ori = 360-(180*math.atan2(lj,lk) / math.pi)        #正转角度
                        if(opposite_rotate == 1):
                            deg_ori = 360-(360-(180*math.atan2(lj,lk) / math.pi))   #反转角度
                        else:
                            deg_ori = 360-(180*math.atan2(lj,lk) / math.pi)        #正转角度
                    if (float(get_G1_match.group(5)) < 0 and float(get_G1_match.group(6)) >0):
                        if(forward_roatate == 1):
                            deg_ori= -180*math.atan2(lj,lk) / math.pi        #正转角度
                        if(opposite_rotate == 1):
                            deg_ori= 360-(-180*math.atan2(lj,lk) / math.pi)   #反转角度
                        else:
                            deg_ori= -180*math.atan2(lj,lk) / math.pi        #正转角度
                    if (float(get_G1_match.group(5)) < 0 and float(get_G1_match.group(6)) < 0):
                        if(forward_roatate == 1):
                            deg_ori = -(180*math.atan2(lj,lk) / math.pi)        #正转角度
                        if(opposite_rotate == 1):
                            deg_ori = 360-(-(180*math.atan2(lj,lk) / math.pi))   #反转角度
                        else:
                            deg_ori = -(180*math.atan2(lj,lk) / math.pi)        #正转角度
                    if (float(get_G1_match.group(5)) > 0 and float(get_G1_match.group(6)) < 0):
                        if(forward_roatate == 1):
                            deg_ori = 360-(180*math.atan2(lj,lk) / math.pi)       #正转角度
                        if(opposite_rotate == 1):
                            deg_ori = 360-(360-(180*math.atan2(lj,lk) / math.pi))  #反转角度
                        else:
                            deg_ori = 360-(180*math.atan2(lj,lk) / math.pi)       #正转角度
                    print(deg_ori)
                    G_4ax_degree.append(deg_ori)
                    deg_count = math.atan2(lj,lk)
                    
                    get_coordinage_change(ly, lz, deg_count)
                    G_4_Axis = axis_style
                    #Gcode_4_style('G01', get_G1_match.group(1), get_G1_match.group(2), get_G1_match.group(3), axis_style, deg_ori, G_speed)
                    Gcode_4_style('G01', lx, rv1, rv2, axis_style, deg_ori, G_speed)
                
                if(float(get_G1_match.group(5)) == 0.0):
                    if(axis_4_append_text == ''):
                        axis_style = 'B'
                    if(axis_4_append_text != ''):
                        axis_style = axis_4_append_text
                    
                    li = float(get_G1_match.group(4))
                    lk = float(get_G1_match.group(6))

                    if (float(get_G1_match.group(4)) >=0 and float(get_G1_match.group(6)) >= 0):
                        if(forward_roatate == 1):
                            deg_ori = 180*math.atan2(li,lk) / math.pi        #正转角度
                        if(opposite_rotate == 1):
                            deg_ori = 360-(180*math.atan2(li,lk) / math.pi)   #反转角度
                        else:
                            deg_ori = 180*math.atan2(li,lk) / math.pi        #正转角度
                    if (float(get_G1_match.group(4)) < 0 and float(get_G1_match.group(6)) >0):
                        if(forward_roatate == 1):
                            deg_ori= 360+180*math.atan2(lj,lk) / math.pi        #正转角度
                        if(opposite_rotate == 1):
                            deg_ori= 360-(360+180*math.atan2(lj,lk) / math.pi)   #反转角度
                        else:
                            deg_ori= 360+180*math.atan2(lj,lk) / math.pi        #正转角度
                    if (float(get_G1_match.group(4)) < 0 and float(get_G1_match.group(6)) < 0):
                        if(forward_roatate == 1):
                            deg_ori= 360+180*math.atan2(lj,lk) / math.pi        #正转角度
                        if(opposite_rotate == 1):
                            deg_ori= 360-(360+180*math.atan2(lj,lk) / math.pi)   #反转角度
                        else:
                            deg_ori= 360+180*math.atan2(lj,lk) / math.pi        #正转角度
                    if (float(get_G1_match.group(4)) > 0 and float(get_G1_match.group(6)) < 0):
                        if(forward_roatate == 1):
                            deg_ori = 180*math.atan2(lj,lk) / math.pi       #正转角度
                        if(opposite_rotate == 1):
                            deg_ori = 360-(180*math.atan2(lj,lk) / math.pi)  #反转角度
                        else:
                            deg_ori = 180*math.atan2(lj,lk) / math.pi       #正转角度
                    G_4ax_degree.append(deg_ori)
                    deg_count = math.atan2(li,lk)
                    get_coordinage_change(lx, lz, deg_count)
                    G_4_Axis = axis_style
                    #Gcode_4_style('G01', get_G1_match.group(1), get_G1_match.group(2), get_G1_match.group(3), axis_style, deg_ori, G_speed)
                    Gcode_4_style('G01', rv1, ly, rv2, axis_style, deg_ori, G_speed)

            else:
                if(G_4_Axis == 'A'):
                    # lj = float(get_G1_match.group(5))
                    # lk = float(get_G1_match.group(6))
                    # deg_count = math.atan2(lj,lk)
                    get_coordinage_change(ly, lz, deg_count)
                    Gcode_4_style('G01', lx, rv1, rv2, G_4_Axis, G_4ax_degree[len(G_4ax_degree)-1], G_speed)
                if(G_4_Axis == 'B'):
                    # li = float(get_G1_match.group(4))
                    # lk = float(get_G1_match.group(6))
                    # deg_count = math.atan2(li,lk)
                    get_coordinage_change(lx, lz, deg_count)
                    Gcode_4_style('G01', rv1, ly, rv2, axis_style, deg_ori, G_speed)

        cnum = cnum + 1

#定义坐标转换函数，稍后用numpy的矩阵操作重写此函数
def get_coordinage_change(lv1, lv2, av1):
    global rv1, rv2
    use_ang = av1  #(av1 * math.pi) / 180
    rv1 = lv1*math.cos(use_ang) - lv2*math.sin(use_ang)
    rv2 = lv2*math.cos(use_ang) + lv1*math.sin(use_ang)
    # lv1 = rv1
    # lv2 = rv2
    # return lv1, lv2

#定义G93速度计算函数，对于速度进行重新计算，xx,yy,zz分别为当前点与前一点的坐标差值，deg为当前点与前一点的角度差值，f为当前速度值，默认，f==dmp_value,所以这里只传递一个值，feed_max为预设的速度最大值，当计算的超过该值，则使用该值
def get_G93_feed_speed(xx,yy,zz,f,feedmax,deg):
    pass
    global counting_time
    global renew_feed
    l_dis = math.sqrt(xx*xx + yy*yy + zz*zz)
    r_dis = abs(deg)  #角度方向的位移，即角度值
    l_time = l_dis / f
    r_time = r_dis / f
    #new_time = l_time + r_time
    if(l_time == 0.0):
        l_feed = 0.0
    else:
        l_feed = 1 / l_time
    
    if(r_dis == 0.0):
        r_feed = 0.0
        renew_feed = l_feed
    else:
        r_feed = 1 / r_time
    
        if(l_feed >= r_feed):
            renew_feed = r_feed
            if(renew_feed >= feed_max):
                renew_feed = feed_max
            counting_time = counting_time + r_time
            renew_feed = renew_feed
        else:
            renew_feed = l_feed
            if(renew_feed >= feed_max):
                renew_feed = feed_max
            counting_time = counting_time + l_time
            renew_feed = renew_feed


#匹配5轴后处理
def match_Feature_line_5axis(wlen, alldata):
    pass

#写程序头部
def Gcode_head_3axis(wlen, alldata, filename):

    cnum = 0
    # g_head = '%_N_{0}_MPF'.format(alldata[0].strip('\n'))
    # G3_new_code.append(g_head)
    # print('the file head is {0}'.format(g_head))
    while cnum < wlen:
        
        get_program_match = pattern_head_programname.match(alldata[cnum])
        get_toolname_match = pattern_head_toolnmae.match(alldata[cnum])
        get_toolparam_match = pattern_head_toolparam.match(alldata[cnum])
        get_holderparam_match = pattern_head_holderparam.match(alldata[cnum])
        get_tool_path_length_match = pattern_head_path_length.match(alldata[cnum])
        get_tool_path_cut_length_match = pattern_head_cut_length.match(alldata[cnum])
        get_tool_path_path_time_match = pattern_head_path_time.match(alldata[cnum])
        get_tool_path_cut_time_match = pattern_head_cut_time.match(alldata[cnum])
        get_load_tool_num_match = pattern_head_load_tool.match(alldata[cnum])
        get_select_tool_num_match = pattern_head_select_tool.match(alldata[cnum])
        get_spindl_match = pattern_Spindl.match(alldata[cnum])
        get_rapid_match = pattern_head_rapid_end.match(alldata[cnum])
        #原生cls需要匹配的两项
        get_tldata_info_match = pattern_tldata_info.match(alldata[cnum])
        get_toolpath_info_match = pattern_toolpath_info.match(alldata[cnum])

        if(get_program_match):
            #print('the program name is {0}'.format(get_program_match.group(1)))
            g_head = '%_N_{0}_MPF'.format(get_program_match.group(1))
            print(g_head)
            G3_new_code.append(g_head)
        
        if(get_toolname_match):
            #print('the tool name is {0}'.format(get_toolname_match.group(1)))
            tool_line = 'M06\nT="{0}"'.format(get_toolname_match.group(1))
            print(tool_line)
            G3_new_code.append(tool_line)

        if(get_holderparam_match):
            #print('the holder under_diameter is {0}'.format(get_holderparam_match.group(1)))
            #print('the holder length is {0}'.format(get_holderparam_match.group(2)))
            #print('the holder angle is {0}'.format(get_holderparam_match.group(3)))
            holder_info = ';Holder_length = {0}'.format(get_holderparam_match.group(2))
            print(holder_info)
            G3_new_code.append(holder_info)

        if(get_toolparam_match):
            #print('the tool length is {0}'.format(get_toolparam_match.group(1)))
            #print('the cut length is {0}'.format(get_toolparam_match.group(2)))
            #print('the diameter of tool is {0}'.format(get_toolparam_match.group(3)))
            #print('the under diameter of tool is {0}'.format(get_toolparam_match.group(4)))
            tool_info = ';TD = {0} R = {1}\n;Tool_Length = {2}'.format(get_toolparam_match.group(3), get_toolparam_match.group(4), get_toolparam_match.group(1))
            print(tool_info)
            G3_new_code.append(tool_info)

        if(get_tool_path_length_match):
            #print('The whole path length is {0}'.format(get_tool_path_length_match.group(1)))
            tool_path_line = ';ToolPathLength = {0:.3f}'.format(float(get_tool_path_length_match.group(1)))
            print(tool_path_line)
            G3_new_code.append(tool_path_line)
            
        if(get_tool_path_cut_length_match):
            #print('The Cutting path length is {0}'.format(get_tool_path_cut_length_match.group(1)))
            tool_cut_path_line = ';ToolPathCuttingLength = {0:.3f}'.format(float(get_tool_path_cut_length_match.group(1)))
            print(tool_cut_path_line)
            G3_new_code.append(tool_cut_path_line)

        if(get_tool_path_path_time_match):
            #print('the whole spending time is: {0} mins'.format(get_tool_path_path_time_match.group(1)))
            tool_path_time_line = ';ToolPathTime = {0:.3f} min'.format(float(get_tool_path_path_time_match.group(1)))
            print(tool_path_time_line)
            G3_new_code.append(tool_path_time_line)

        if(get_tool_path_cut_time_match):
            #print('the cutting spending time is {0} mins'.format(get_tool_path_cut_time_match.group(1)))
            tool_path_cut_time_line = ';ToolPathCuttingTime = {0:.3f} min'.format(float(get_tool_path_cut_time_match.group(1)))
            print(tool_path_cut_time_line)
            G3_new_code.append(tool_path_cut_time_line)

        #原生cls文件匹配的两项
        if(get_tldata_info_match):
            #print('the TLdata Diameter is {0}'.format(get_tldata_info_match.group(1)))
            #print('the TLdata under Diameter is {0}'.format(get_tldata_info_match.group(2)))
            #print('the TLdata whole length is {0}'.format(get_tldata_info_match.group(3)))
            ToolData = ';Current Tool Data: Dia={0:.3f} Rad={1:.3f} Length={2:.3f}'.format(float(get_tldata_info_match.group(1)), float(get_tldata_info_match.group(2)), float(get_tldata_info_match.group(3)))
            print(ToolData)
            G3_new_code.append(ToolData)

        if(get_toolpath_info_match):
            #print('the tool path info process name is {0}'.format(get_toolpath_info_match.group(1)))
            #print('the tool path info tool name is {0}'.format(get_toolpath_info_match.group(2)))
            ToolProcessName = ';Current Tool:  {0}  Current Process:  {1}'.format(get_toolpath_info_match.group(2), get_toolpath_info_match.group(1))
            print(ToolProcessName)
            G3_new_code.append(ToolProcessName)
            

        if(get_load_tool_num_match):
            #print('the load tool number is {0}'.format(get_load_tool_num_match.group(1)))
            load_tool_line = ';Load The Tool Number is {0:d}'.format(int(get_load_tool_num_match.group(1)))
            print(load_tool_line)
            G3_new_code.append(load_tool_line)

        if(get_select_tool_num_match):
            #print('the select tool number is {0}'.format(get_select_tool_num_match.group(1)))
            select_tool_line = ';M06 T{0:d}'.format(int(get_select_tool_num_match.group(1)))
            print(select_tool_line)
            G3_new_code.append(select_tool_line)

        if(get_spindl_match):
            spindl_line = 'S{0:.3f} M03'.format(float(get_spindl_match.group(1)))
            print(spindl_line)
            G3_new_code.append(spindl_line)

        if(get_rapid_match):
            #推出头部信息查询
            abs_line = 'G90'
            original_line = 'G54'
            plane_line ='G17'
            G3_new_code.append(abs_line)
            G3_new_code.append(original_line)
            G3_new_code.append(plane_line)
            break

        cnum = cnum + 1

def Gcode_head_4axis(wlen, alldata, filename):
    pass
    cnum = 0
    # g_head = '%_N_{0}_MPF'.format(alldata[0].strip('\n'))
    # G3_new_code.append(g_head)
    # print('the file head is {0}'.format(g_head))
    while cnum < wlen:
        
        get_program_match = pattern_head_programname.match(alldata[cnum])
        get_toolname_match = pattern_head_toolnmae.match(alldata[cnum])
        get_toolparam_match = pattern_head_toolparam.match(alldata[cnum])
        get_holderparam_match = pattern_head_holderparam.match(alldata[cnum])
        get_tool_path_length_match = pattern_head_path_length.match(alldata[cnum])
        get_tool_path_cut_length_match = pattern_head_cut_length.match(alldata[cnum])
        get_tool_path_path_time_match = pattern_head_path_time.match(alldata[cnum])
        get_tool_path_cut_time_match = pattern_head_cut_time.match(alldata[cnum])
        get_load_tool_num_match = pattern_head_load_tool.match(alldata[cnum])
        get_select_tool_num_match = pattern_head_select_tool.match(alldata[cnum])
        get_spindl_match = pattern_Spindl.match(alldata[cnum])
        get_rapid_match = pattern_head_rapid_end.match(alldata[cnum])
        #原生cls需要匹配的两项
        get_tldata_info_match = pattern_tldata_info.match(alldata[cnum])
        get_toolpath_info_match = pattern_toolpath_info.match(alldata[cnum])

        if(get_program_match):
            #print('the program name is {0}'.format(get_program_match.group(1)))
            g_head = '%_N_{0}_MPF'.format(get_program_match.group(1))
            print(g_head)
            G4_new_code.append(g_head)
        
        if(get_toolname_match):
            #print('the tool name is {0}'.format(get_toolname_match.group(1)))
            tool_line = 'M06\nT="{0}"'.format(get_toolname_match.group(1))
            print(tool_line)
            G4_new_code.append(tool_line)

        if(get_holderparam_match):
            #print('the holder under_diameter is {0}'.format(get_holderparam_match.group(1)))
            #print('the holder length is {0}'.format(get_holderparam_match.group(2)))
            #print('the holder angle is {0}'.format(get_holderparam_match.group(3)))
            holder_info = ';Holder_length = {0}'.format(get_holderparam_match.group(2))
            print(holder_info)
            G4_new_code.append(holder_info)

        if(get_toolparam_match):
            #print('the tool length is {0}'.format(get_toolparam_match.group(1)))
            #print('the cut length is {0}'.format(get_toolparam_match.group(2)))
            #print('the diameter of tool is {0}'.format(get_toolparam_match.group(3)))
            #print('the under diameter of tool is {0}'.format(get_toolparam_match.group(4)))
            tool_info = ';TD = {0} R = {1}\n;Tool_Length = {2}'.format(get_toolparam_match.group(3), get_toolparam_match.group(4), get_toolparam_match.group(1))
            print(tool_info)
            G4_new_code.append(tool_info)

        if(get_tool_path_length_match):
            #print('The whole path length is {0}'.format(get_tool_path_length_match.group(1)))
            tool_path_line = ';ToolPathLength = {0:.3f}'.format(float(get_tool_path_length_match.group(1)))
            print(tool_path_line)
            G4_new_code.append(tool_path_line)
            
        if(get_tool_path_cut_length_match):
            #print('The Cutting path length is {0}'.format(get_tool_path_cut_length_match.group(1)))
            tool_cut_path_line = ';ToolPathCuttingLength = {0:.3f}'.format(float(get_tool_path_cut_length_match.group(1)))
            print(tool_cut_path_line)
            G4_new_code.append(tool_cut_path_line)

        if(get_tool_path_path_time_match):
            #print('the whole spending time is: {0} mins'.format(get_tool_path_path_time_match.group(1)))
            tool_path_time_line = ';ToolPathTime = {0:.3f} min'.format(float(get_tool_path_path_time_match.group(1)))
            print(tool_path_time_line)
            G4_new_code.append(tool_path_time_line)

        if(get_tool_path_cut_time_match):
            #print('the cutting spending time is {0} mins'.format(get_tool_path_cut_time_match.group(1)))
            tool_path_cut_time_line = ';ToolPathCuttingTime = {0:.3f} min'.format(float(get_tool_path_cut_time_match.group(1)))
            print(tool_path_cut_time_line)
            G4_new_code.append(tool_path_cut_time_line)

        #原生cls文件匹配的两项
        if(get_tldata_info_match):
            #print('the TLdata Diameter is {0}'.format(get_tldata_info_match.group(1)))
            #print('the TLdata under Diameter is {0}'.format(get_tldata_info_match.group(2)))
            #print('the TLdata whole length is {0}'.format(get_tldata_info_match.group(3)))
            ToolData = ';Current Tool Data: Dia={0:.3f} Rad={1:.3f} Length={2:.3f}'.format(float(get_tldata_info_match.group(1)), float(get_tldata_info_match.group(2)), float(get_tldata_info_match.group(3)))
            print(ToolData)
            G4_new_code.append(ToolData)

        if(get_toolpath_info_match):
            #print('the tool path info process name is {0}'.format(get_toolpath_info_match.group(1)))
            #print('the tool path info tool name is {0}'.format(get_toolpath_info_match.group(2)))
            ToolProcessName = ';Current Tool:  {0}  Current Process:  {1}'.format(get_toolpath_info_match.group(2), get_toolpath_info_match.group(1))
            print(ToolProcessName)
            G4_new_code.append(ToolProcessName)
            

        if(get_load_tool_num_match):
            #print('the load tool number is {0}'.format(get_load_tool_num_match.group(1)))
            load_tool_line = ';Load The Tool Number is {0:d}'.format(int(get_load_tool_num_match.group(1)))
            print(load_tool_line)
            G4_new_code.append(load_tool_line)

        if(get_select_tool_num_match):
            #print('the select tool number is {0}'.format(get_select_tool_num_match.group(1)))
            select_tool_line = ';M06 T{0:d}'.format(int(get_select_tool_num_match.group(1)))
            print(select_tool_line)
            G4_new_code.append(select_tool_line)

        if(get_spindl_match):
            spindl_line = 'S{0:.3f} M03'.format(float(get_spindl_match.group(1)))
            print(spindl_line)
            G4_new_code.append(spindl_line)

        if(get_rapid_match):
            #推出头部信息查询
            pre_head = '%'
            pre_name = 'O9001'
            abs_line = 'G21\nG40 G17 G49 G80 G90'
            original_line = 'M26\nG05.1 Q1'
            speed_style = 'G94'
            start_line ='G91 G28 Z0.0'
            last_ph = 'G43 Z60 H4'
            G4_new_code.append(pre_head)
            G4_new_code.append(pre_name)
            G4_new_code.append(abs_line)
            G4_new_code.append(original_line)
            G4_new_code.append(speed_style)
            G4_new_code.append(start_line)
            G4_new_code.append(last_ph)
            break

        cnum = cnum + 1
    

def Gcode_head_5axis():
    pass

    
#写程序尾部
def Gcode_toend(filename):
    stop_rotating_line = 'M05'
    stop_program_line = 'M30'
    cls_name = filename + '.cls'
    #len_of_cls = len(cls_name)
    end_info = ';The source file is located in: {0}'.format(cls_name)
    print(stop_rotating_line)
    print(stop_program_line)
    print(end_info)
    G3_new_code.append(stop_rotating_line)
    G3_new_code.append(stop_program_line)
    G3_new_code.append(end_info)


def Gcode_4axis_toend(filename):
    pass
    pre_toend = 'G91 G28 Z0.0'
    stop_rotating_line = 'M05\nM09'
    stop_midlle_line = 'G05.1 Q0.0\nG94'
    stop_program_line = 'M09\nM30'
    cls_name = filename + '.cls'
    end_info = ';The source file is located in: {0}'.format(cls_name)
    print(pre_toend)
    print(stop_rotating_line)
    print(stop_midlle_line)
    print(stop_program_line)
    print(end_info)
    G4_new_code.append(pre_toend)
    G4_new_code.append(stop_rotating_line)
    G4_new_code.append(stop_midlle_line)
    G4_new_code.append(stop_program_line)
    G4_new_code.append(end_info)

#3轴程序坐标输出模式
def Gcode_3_style(head_line, x, y, z, F):
    pass
    try:
        #st1 = head_line + ' ' + 'X' + str(x) + ' ' + 'Y' + str(y) + ' ' + 'Z' + str(z) + ' ' + 'F' + str(F)
        st1 = '{0} X{1:.3f} Y{2:.3f} Z{3:.3f} F{4:.3f}'.format(head_line, float(x), float(y), float(z), float(F))
        print(st1)
        G3_code.append(st1)
    except:
        print('It looks something wrong happend!.....')

def Gcode_3_circle_style(head_line, w_plane, x, y, z, i, j, k, F):
    try:
        pass
        if(w_plane == 'G17'):
            #st2 = "{0} X{1:.3f} Y{2:.3f} Z{3:.3f} I{4:.3f} J{5:.3f} F{6:.3f}".format(head_line, float(x), float(y), float(z), float(i), float(j), float(F)) 
            st2 = "{0} X{1:.3f} Y{2:.3f} Z{3:.3f} I{4:.3f} J{5:.3f} F{6:.3f}".format(head_line, float(x), float(y), float(z), float(i), float(j), float(F))
            print(st2)
            G3_code.append(st2)
        if(w_plane == 'G18'):
            
            #st2 = head_line + ' ' + 'X' + str(x) + ' ' + 'Y' + str(y) + ' ' + 'Z' + str(z) + ' ' + 'I' + str(i) + ' ' + 'K' + str(k) + 'F' + str(F)
            st2 = "{0} X{1:.3f} Y{2:.3f} Z{3:.3f} I{4:.3f} K{5:.3f} F{6:.3f}".format(head_line, float(x), float(y), float(z), float(i), float(k), float(F))
            G3_code.append(st2)
        if(w_plane == 'G19'):
            #st2 = head_line + ' ' + 'X' + str(x) + ' ' + 'Y' + str(y) + ' ' + 'Z' + str(z) + ' ' + 'J' + str(j) + ' ' + 'K' + str(k) + 'F' + str(F)
            st2 = "{0} X{1:.3f} Y{2:.3f} Z{3:.3f} J{4:.3f} K{5:.3f} F{6:.3f}".format(head_line, float(x), float(y), float(z), float(j), float(k), float(F))
            G3_code.append(st2)
        
    except:
          print('It looks something wrong happend!.....') 

#4轴程序坐标输出模式
def Gcode_4_style(head_line, x, y, z, axis_style, ang1, F):
    #pass
    try:
        # if(axis_style == 'A'):
        #     #st1 = head_line + ' ' + 'X' + str(x) + ' ' + 'Y' + str(y) + ' ' + 'Z' + str(z) + ' ' + 'A' + str(ang1) + ' ' + 'F' + str(F)
        #     st1 = '{0} X{1:.3f} Y{2:.3f} Z{3:.3f} A{4:.3f} F{5:.3f}'.format(head_line, x, y, z, float(ang1), float(F))
        #     print(st1)
        #     G4_code.append(st1)
        # if(axis_style == 'B'):
        #    #st1 = head_line + ' ' + 'X' + str(x) + ' ' + 'Y' + str(y) + ' ' + 'Z' + str(z) + ' ' + 'B' + str(ang1) + ' ' + 'F' + str(F)
        #     st1 = '{0} X{1:.3f} Y{2:.3f} Z{3:.3f} B{4:.3f} F{5:.3f}'.format(head_line, x, y, z, float(ang1), float(F))
        #     print(st1)
        #     G4_code.append(st1)
        st1 = '{0} X{1:.3f} Y{2:.3f} Z{3:.3f} {4}{5:.3f} F{6:.3f}'.format(head_line, x, y, z, axis_style, float(ang1), float(F))
        print(st1)
        G4_code.append(st1)
            
        
         
    except:
        print('It looks something wrong happend!.....')

#5轴程序坐标输出模式
def Gcode_5_style(head_line, x, y, z, ang1, ang2, F):
    pass

#4轴坐标值转换, 使用numpy矩阵计算机型坐标表换计算
def get_4_coordinate(v1, v2, delta):
    #pass
    ues_delta = (delta * math.pi) / 180
    nv1 = v1 * math.cos(ues_delta) - v2 * math.sin(ues_delta)
    nv2 = v2 * math.cos(ues_delta) + v1 * math.sin(ues_delta)
    v1 = nv1
    v2 = nv2

#4轴角度计算
def count_4_angle_degree():
    pass

#5轴角度计算
def count_5_angle_degree():
    pass


#定义输出函数
def output_Gcode(post_name, using_path):
    print('Post is Starting......')
    #print('The length of Out_List is : ' + str(len(G4_code)))
    #屏幕打印输出测试代码

    G3_new_code.append(G3_code[0])
    get_G3_oldline = pattern_G3_new_output_line.match(G3_code[0])
    pre_head = get_G3_oldline.group(1)
    pre_x = get_G3_oldline.group(2)
    pre_y = get_G3_oldline.group(3)
    pre_z = get_G3_oldline.group(4)
    pre_f = get_G3_oldline.group(5)

    for i in range(1, len(G3_code)):
        #print(G3_code[i])
        get_G3_oldline_head = pattern_G3_new_output_head.match(G3_code[i])
        if(get_G3_oldline_head.group(1) == 'G00' or get_G3_oldline_head.group(1) == 'G01'):
            get_G3_oldline_line = pattern_G3_new_output_line.match(G3_code[i])
            if(get_G3_oldline_line):
                temp_head = get_G3_oldline_line.group(1)
                tempx = get_G3_oldline_line.group(2)
                tempy = get_G3_oldline_line.group(3)
                tempz = get_G3_oldline_line.group(4)
                tempF = get_G3_oldline_line.group(5)

                temp_line = G3_code[i]

                if(temp_head == pre_head):
                    rem1 = temp_line.replace(temp_head, '')
                    temp_line = rem1
                    
                if(tempx == pre_x):
                    rem2 = temp_line.replace(tempx, '')
                    temp_line = rem2
                if(tempy == pre_y):
                    rem3 = temp_line.replace(tempy, '')
                    temp_line = rem3
                if(tempz == pre_z):
                    rem4 = temp_line.replace(tempz, '')
                    temp_line = rem4
                if(tempF == pre_f):
                    rem5 = temp_line.replace(tempF, '')
                    temp_line = rem5
            print('Out put line: ' + temp_line.strip())
            G3_new_code.append(temp_line.strip())

            pre_head = temp_head
            pre_x = tempx
            pre_y = tempy
            pre_z = tempz
            pre_f = tempF

        if(get_G3_oldline_head.group(1) == 'G02' or get_G3_oldline_head.group(1) == 'G03'):
            get_G3_oldline_circle_G17 = pattern_G3_new_output_circle_G17.match(G3_code[i])
            get_G3_oldline_circle_G18 = pattern_G3_new_output_circle_G18.match(G3_code[i])
            get_G3_oldline_circle_G19 = pattern_G3_new_output_circle_G19.match(G3_code[i])

            if(get_G3_oldline_circle_G17):
                temp_head = get_G3_oldline_circle_G17.group(1)
                tempx = get_G3_oldline_circle_G17.group(2)
                tempy = get_G3_oldline_circle_G17.group(3)
                tempz = get_G3_oldline_circle_G17.group(4)
                tempF = get_G3_oldline_circle_G17.group(5)

                temp_line = G3_code[i]

                if(temp_head == pre_head):
                    rem1 = temp_line.replace(temp_head, '')
                    temp_line = rem1
                    
                if(tempx == pre_x):
                    rem2 = temp_line.replace(tempx, '')
                    temp_line = rem2
                if(tempy == pre_y):
                    rem3 = temp_line.replace(tempy, '')
                    temp_line = rem3
                if(tempz == pre_z):
                    rem4 = temp_line.replace(tempz, '')
                    temp_line = rem4
                if(tempF == pre_f):
                    rem5 = temp_line.replace(tempF, '')
                    temp_line = rem5

                print('Out put line: ' + temp_line.strip())
                G3_new_code.append(temp_line.strip())

                pre_head = temp_head
                pre_x = tempx
                pre_y = tempy
                #pre_z = tempz
                pre_f = tempF

            if(get_G3_oldline_circle_G18):
                temp_head = get_G3_oldline_circle_G18.group(1)
                tempx = get_G3_oldline_circle_G18.group(2)
                tempy = get_G3_oldline_circle_G18.group(3)
                tempz = get_G3_oldline_circle_G18.group(4)
                tempF = get_G3_oldline_circle_G18.group(5)

                temp_line = G3_code[i]

                if(temp_head == pre_head):
                    rem1 = temp_line.replace(temp_head, '')
                    temp_line = rem1
                    
                if(tempx == pre_x):
                    rem2 = temp_line.replace(tempx, '')
                    temp_line = rem2
                if(tempy == pre_y):
                    rem3 = temp_line.replace(tempy, '')
                    temp_line = rem3
                if(tempz == pre_z):
                    rem4 = temp_line.replace(tempz, '')
                    temp_line = rem4
                if(tempF == pre_f):
                    rem5 = temp_line.replace(tempF, '')
                    temp_line = rem5

                print('Out put line: ' + temp_line.strip())
                G3_new_code.append(temp_line.strip())

                pre_head = temp_head
                pre_x = tempx
                #pre_y = tempy
                pre_z = tempz
                pre_f = tempF

            if(get_G3_oldline_circle_G19):
                temp_head = get_G3_oldline_circle_G19.group(1)
                tempx = get_G3_oldline_circle_G19.group(2)
                tempy = get_G3_oldline_circle_G19.group(3)
                tempz = get_G3_oldline_circle_G19.group(4)
                tempF = get_G3_oldline_circle_G19.group(5)

                temp_line = G3_code[i]

                if(temp_head == pre_head):
                    rem1 = temp_line.replace(temp_head, '')
                    temp_line = rem1
                    
                if(tempx == pre_x):
                    rem2 = temp_line.replace(tempx, '')
                    temp_line = rem2
                if(tempy == pre_y):
                    rem3 = temp_line.replace(tempy, '')
                    temp_line = rem3
                if(tempz == pre_z):
                    rem4 = temp_line.replace(tempz, '')
                    temp_line = rem4
                if(tempF == pre_f):
                    rem5 = temp_line.replace(tempF, '')
                    temp_line = rem5
                print('Out put line: ' + temp_line.strip())
                G3_new_code.append(temp_line.strip())

                pre_head = temp_head
                #pre_x = tempx
                pre_y = tempy
                pre_z = tempz
                pre_f = tempF

        
            

    Gcode_toend(post_name)
    #将输出的代码写入一个文本中
    #filename = r'E:\\G93分析资料\\Infot.nc'
    #filename = r'D:\\VCTEST\\G93分析资料\\Infot.nc'
    filename = using_path + '/' + post_name + '.nc'
    output_file = open(filename, 'w+')
    for j in range(len(G3_new_code)):
        #output_file.writelines(G3_code[j] + '\n')
        output_file.writelines(G3_new_code[j] + '\n')
        print(G3_new_code[j])
    output_file.close()


def output_4x_Gcode(post_name, using_path):
    pass
    print('4 Axis Post is Starting.......:')
    
    get_G4_oldline = pattern_G4_oldline.match(G4_code[0])
    pre_head = get_G4_oldline.group(1)
    pre_x = get_G4_oldline.group(2)
    pre_y = get_G4_oldline.group(3)
    pre_z = get_G4_oldline.group(4)
    pre_rotate_ax = get_G4_oldline.group(5)
    pre_angle = get_G4_oldline.group(6)
    pre_feed = get_G4_oldline.group(7)
    G4_code[0] = G4_code[0].replace('F'+pre_feed, '')
    
    G4_G0_head_style = 'G00 G90 X{0:.3f} Y{1:.3f} {2}{3}\nG43 Z{4:.3f} H04'.format(float(pre_x), float(pre_y), pre_rotate_ax, pre_angle, float(pre_z))
    #G4_new_code.append(G4_code[0])
    G4_new_code.append(G4_G0_head_style)
    print(G4_code[0])

    for j in range(1, len(G4_code)):
        get_G4_oldline = pattern_G4_oldline.match(G4_code[j])
        if(get_G4_oldline):
            if(get_G4_oldline.group(1) == 'G00'):
                pass
                temp_head = get_G4_oldline.group(1)
                temp_x = get_G4_oldline.group(2)
                temp_y = get_G4_oldline.group(3)
                temp_z = get_G4_oldline.group(4)
                temp_rotate_ax = get_G4_oldline.group(5)
                temp_angle = get_G4_oldline.group(6)
                temp_feed = get_G4_oldline.group(7)

                temp_line = G4_code[j]

                temp_line = temp_line.replace('F'+temp_feed, '')
                if(temp_head == pre_head):
                    rem1 = temp_line.replace(temp_head, '')
                    temp_line = rem1 

                if(temp_x == pre_x):
                    rem2 = temp_line.replace('X' + temp_x, '')
                    temp_line = rem2

                if(temp_y == pre_y):
                    rem3 = temp_line.replace('Y' + temp_y, '')
                    temp_line = rem3

                if(temp_z == pre_z):
                    rem4 = temp_line.replace('Z' + temp_z, '')
                    temp_line = rem4

                if(temp_rotate_ax == pre_rotate_ax):
                    rem5 = temp_line.replace(temp_rotate_ax, '')
                    temp_line = rem5

                if(temp_angle == pre_angle):
                    rem6 = temp_line.replace(temp_angle, '')
                    temp_line = rem6

                
                print('out line is : ' + temp_line)
                G4_new_code.append(temp_line.strip())

                pre_head = temp_head
                pre_x = temp_x
                pre_y = temp_y
                pre_z = temp_z
                pre_rotate_ax = temp_rotate_ax
                pre_angle = temp_angle
                pre_feed = temp_feed

            if(get_G4_oldline.group(1) == 'G01'):
                pass
                temp_head = get_G4_oldline.group(1)
                temp_x = get_G4_oldline.group(2)
                temp_y = get_G4_oldline.group(3)
                temp_z = get_G4_oldline.group(4)
                temp_rotate_ax = get_G4_oldline.group(5)
                temp_angle = get_G4_oldline.group(6)
                temp_feed = get_G4_oldline.group(7)

                gx = float(temp_x) - float(pre_x)
                gy = float(temp_y) - float(pre_y)
                gz = float(temp_z) - float(pre_z)
                gf = float(temp_feed)
                gdeg = float(temp_angle) - float(pre_angle)

                get_G93_feed_speed(gx,gy,gz,gf,feed_max,gdeg)

                temp_line = G4_code[j]
                renew_feed_style = '{0:.3f}'.format(renew_feed)
                rem = temp_line.replace(temp_feed, str(renew_feed_style))
                temp_line = rem

                if(temp_head == pre_head):
                    rem1 = temp_line.replace(temp_head, '')
                    temp_line = rem1 

                if(temp_x == pre_x):
                    rem2 = temp_line.replace('X'+temp_x, '')
                    temp_line = rem2

                if(temp_y == pre_y):
                    rem3 = temp_line.replace('Y'+temp_y, '')
                    temp_line = rem3

                if(temp_z == pre_z):
                    rem4 = temp_line.replace('Z'+temp_z, '')
                    temp_line = rem4

                # if(temp_rotate_ax == pre_rotate_ax):
                #     rem5 = temp_line.replace(temp_rotate_ax, '')
                #     temp_line = rem5

                if(temp_angle == pre_angle):
                    rem6 = temp_line.replace(temp_rotate_ax+temp_angle, '')
                    temp_line = rem6

                

                print('out line is : ' + temp_line)
                G4_new_code.append(temp_line.strip())
                pre_head = temp_head
                pre_x = temp_x
                pre_y = temp_y
                pre_z = temp_z
                pre_rotate_ax = temp_rotate_ax
                pre_angle = temp_angle
                pre_feed = temp_feed


    Gcode_4axis_toend(post_name)
    #将输出的代码写入一个文本中
    #filename = r'E:\\G93分析资料\\Infot.nc'
    #filename = r'D:\\VCTEST\\G93分析资料\\Infot.nc'
    filename = using_path + '/' + post_name + '.nc'
    print('the filename is ' + filename)
    output_file = open(filename, 'w+')
    for j in range(len(G4_new_code)):
        #output_file.writelines(G3_code[j] + '\n')
        output_file.writelines(G4_new_code[j] + '\n')
        print(G4_new_code[j])
    output_file.close()



def window_form():

    root = Tk()

    #定义初始化窗体的尺寸,及相关参数
    root.geometry('900x800')
    root.title('Post_NC')
    write_names = []

    def open_it():
        #pass
        global forward_roatate
        global opposite_rotate
        global axis_4_append_text
        global axis_5_append_text

        filenames = tkinter.filedialog.askopenfilenames(filetypes=[("CLS file", "*.cls"), ("all", "*.*")]) ##filenames是一个元祖类型数据
        #global write_names
        p_temp = filenames[0].split('/')
        ff_name = p_temp[len(p_temp)-1]
        p_temp.remove(ff_name)
        select_path = '/'.join(p_temp)
        
        #print(select_path)  提取文件所在路径
        sel_path.config(text=select_path)
        forward_roatate = rotate_forward.get()
        opposite_rotate = rotate_opposite.get()
        axis_4_append_text = axis_4_entry.get()
        axis_5_append_text = axis_5_entry.get()

        #进行几轴程序后处理的判断
        if(check_3_state.get() == 1):
            if(len(filenames) != 0):
                
                for i in range(len(filenames)):
                
                    file_fullname = filenames[i]
                    readWholeFile_3axis(file_fullname)
                    last_name = []
                    last_name = filenames[i].split('/')
                    last_name_temp = last_name[len(last_name)-1].split('.')
                    last_name_without_sytle = last_name_temp[0]
                    write_names.append(last_name_without_sytle)
                    print('the using name is: ' + last_name_without_sytle)
                    sel_list.insert(tkinter.END, file_fullname)
            else:
                sel_path.config(text='没有选择文件')

        if(check_4_state.get() == 1):
            pass
            if(len(filenames) != 0):
                
                for i in range(len(filenames)):
                
                    file_fullname = filenames[i]
                    readWholeFile_4axis(file_fullname)
                    last_name = []
                    last_name = filenames[i].split('/')
                    last_name_temp = last_name[len(last_name)-1].split('.')
                    last_name_without_sytle = last_name_temp[0]
                    write_names.append(last_name_without_sytle)
                    print('the using name is: ' + last_name_without_sytle)
                    sel_list.insert(tkinter.END, file_fullname)
            else:
                sel_path.config(text='没有选择文件')

        if(check_5_state.get() == 1):
            pass
            if(len(filenames) != 0):
                
                for i in range(len(filenames)):
                
                    file_fullname = filenames[i]
                    readWholeFile_5axis(file_fullname)
                    last_name = []
                    last_name = filenames[i].split('/')
                    last_name_temp = last_name[len(last_name)-1].split('.')
                    last_name_without_sytle = last_name_temp[0]
                    write_names.append(last_name_without_sytle)
                    print('the using name is: ' + last_name_without_sytle)
                    sel_list.insert(tkinter.END, file_fullname)
            else:
                sel_path.config(text='没有选择文件')


        if(check_3_state.get() == 0 and check_4_state.get() == 0 and check_5_state.get() == 0):
            print("You do not choose any style to Post the program!......")

        

    def save_it():
        if(check_3_state.get() == 1):
            save_path = tkinter.filedialog.askdirectory()
            #output_show_list = []
            out_path.config(text=save_path)
            for k in range(len(write_names)):
                output_Gcode(write_names[k], save_path)
                output_whole_file =save_path + '/' + write_names[k] + '.nc'
                #output_show_list.append(output_whole_file)
                out_list.insert(tkinter.END, output_whole_file)

        if(check_4_state.get() == 1):
            save_path = tkinter.filedialog.askdirectory()
            #output_show_list = []
            out_path.config(text=save_path)
            for k in range(len(write_names)):
                output_4x_Gcode(write_names[k], save_path)
                output_whole_file =save_path + '/' + write_names[k] + '.nc'
                #output_show_list.append(output_whole_file)
                out_list.insert(tkinter.END, output_whole_file)
        




    #定义窗体布局
    out_file_btn = Button(root, text='选择要后处理的CLS文件：', command=open_it)
    out_file_btn.grid(row=0, column=0, padx=5, pady=5, sticky=W)

    save_file_btn = Button(root, text='选择要后处理文件的位置：', command=save_it)
    save_file_btn.grid(row=2, column=0, padx=5, pady=5, sticky=W)

    sel_path = Label(root, text='show the select path')
    sel_path.grid(row=0, column=1, sticky=W)

    out_path = Label(root, text='show the save path')
    out_path.grid(row=2, column=1, sticky=W)


    lable_mid2 = Label(root, text='')
    lable_mid2.grid(row=3, column=0, sticky=W, rowspan=2)

    text_frame = tkinter.Frame(root, height=100)
    text_frame.grid(row=5, column=1, sticky=W)

    sel_label = Label(text_frame, text='选择的文件：')
    sel_label.grid(row=0, column=1, sticky=W, padx=5, pady=5)
    out_label = Label(text_frame, text='输出的文件：')
    out_label.grid(row=0, column=2, sticky=W, padx=5, pady=5)

    check_frame = tkinter.Frame(root, width=50, height=10)
    check_frame.grid(row=3, column=1)

    check_3_state = tkinter.IntVar()
    check_3ax = Checkbutton(check_frame, text='3 AXIS', variable=check_3_state, state=NORMAL, relief=RIDGE, width=10)
    check_3ax.grid(row=3, column=0)

    check_4_state = tkinter.IntVar()
    check_4ax = Checkbutton(check_frame, text='4 AXIS', variable=check_4_state, state=NORMAL, relief=RIDGE, width=10)
    check_4ax.grid(row=3, column=2)

    check_5_state = tkinter.IntVar()
    check_5ax = Checkbutton(check_frame, text='5 AXIS', variable=check_5_state, state=NORMAL, relief=RIDGE, width=10)
    check_5ax.grid(row=3, column=4, sticky=W)

    axis_4_label = Label(check_frame, text='替换第4轴输出内容')
    axis_4_label.grid(row=4, column=0, sticky=W)

    axis_4_entry = Entry(check_frame)
    axis_4_entry.grid(row=4, column=2)

    axis_5_label = Label(check_frame, text='替换第5轴输出内容')
    axis_5_label.grid(row=5, column=0)

    axis_5_entry = Entry(check_frame)
    axis_5_entry.grid(row=5, column=2)

    rotate_forward = tkinter.IntVar()
    rotate_direction_forward = Checkbutton(check_frame, text='正向', variable=rotate_forward, state=NORMAL, relief=RIDGE)
    rotate_direction_forward.grid(row=6, column=0)

    rotate_opposite = tkinter.IntVar()
    rotate_direction_opposite = Checkbutton(check_frame, text='负向', variable=rotate_opposite, state=NORMAL, relief=RIDGE)
    rotate_direction_opposite.grid(row=6, column=4)

    sel_list = tkinter.Listbox(text_frame, width=50, height=50)  #这里为了能有返回值，不能一行内使用grid属性，
    sel_list.grid(row=1, column=1, sticky=W)
    out_list = tkinter.Listbox(text_frame, width=50, height=50)
    out_list.grid(row=1, column=2, sticky=W)

    Input_frame = tkinter.Frame(root)
    Input_frame.grid(row=4, column=1)

    head_label = Label(Input_frame, text='前置输入')
    head_label.grid(row=0, column=0, sticky=W)
    end_label = Label(Input_frame, text='后置输入')
    end_label.grid(row=0, column=3, sticky=W) 
    pre_input_text = tkinter.Text(Input_frame, height=10, width=50)
    pre_input_text.grid(row=1, column=0, sticky=W)

    after_input_text = tkinter.Text(Input_frame, height=10, width=50)
    after_input_text.grid(row=1, column=3, sticky=W)

    root.mainloop()



if __name__ == "__main__":
    
    window_form()
    #readWholeFile('TEST77.cls')
    #print('the length of Gcode is: ' + str(len(G4_code)))
    #output_Gcode()
    
    
    print("All Things Is Done!......")
