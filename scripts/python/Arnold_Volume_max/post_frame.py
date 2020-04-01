#-*- coding:utf-8 -*-

import os
import hou

hip_dir = os.path.expandvars("$HIP")
log_dir = "/script/sim_log/"

density_log = hip_dir + log_dir + "density.txt"
temperature_log = hip_dir + log_dir + "temperature.txt"
heat_log = hip_dir + log_dir + "heat.txt"

padding = 4

density_max = str(hou.hscriptExpression('volumemax(0,0)'))
density_max = density_max.split('.')
density_max = density_max[0].zfill(padding) + '.' + density_max[1][:2]

temperature_max = str(hou.hscriptExpression('volumemax(0,1)'))
temperature_max = temperature_max.split('.')
temperature_max = temperature_max[0].zfill(padding) + '.' + temperature_max[1][:2]

heat_max = str(hou.hscriptExpression('volumemax(0,2)'))
heat_max = heat_max.split('.')
heat_max = heat_max[0].zfill(padding) + '.' + heat_max[1][:2]



with open(density_log, 'a') as density_log_file:
  density_log_file.write(density_max + "\n")

with open(temperature_log, 'a') as temperature_log_file:
  temperature_log_file.write(temperature_max + "\n")

with open(heat_log, 'a') as heat_log_file:
  heat_log_file.write(heat_max + "\n")
