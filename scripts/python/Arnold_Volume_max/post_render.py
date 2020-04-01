#-*- coding:utf-8 -*-

import os
import hou

hip_dir = hou.hscriptExpression('$HIP')
log_dir = '/script/sim_log/'
node_name = hou.hscriptExpression('opname("..")')

ver = hou.hscriptExpression('$VER')
wipver = hou.hscriptExpression('$WIPVER')


density_log = open(hip_dir + log_dir + 'density.txt', 'r')
density_lead = density_log.readlines()
# 개행문자 제거
density_lead = list(map(lambda s: s.strip(), density_lead))
density_max = max(density_lead)

temperature_log = open(hip_dir + log_dir + 'temperature.txt', 'r')
temperature_lead = temperature_log.readlines()
# 개행문자 제거
temperature_lead = list(map(lambda s: s.strip(), temperature_lead))
temperature_max = max(temperature_lead)

heat_log = open(hip_dir + log_dir + 'heat.txt', 'r')
heat_lead = heat_log.readlines()
# 개행문자 제거
heat_lead = list(map(lambda s: s.strip(), heat_lead))
heat_max = max(heat_lead)


# 정수 패딩 제거
density_max = density_max.replace('0', ' ').lstrip().replace(' ', '0')
temperature_max = temperature_max.replace('0', ' ').lstrip().replace(' ', '0')
heat_max = heat_max.replace('0', ' ').lstrip().replace(' ', '0')


max_log_dir = hip_dir + "/script/" + node_name + '_v' + ver.zfill(2) + '_w' + wipver.zfill(2) + '_' +"max_log.txt"


with open(max_log_dir, 'w') as max_log:
    max_log.write('density: ' + str(density_max) + "\n")
    max_log.write('temperature: ' + str(temperature_max) + "\n")
    max_log.write('heat: ' + str(heat_max) + "\n")
