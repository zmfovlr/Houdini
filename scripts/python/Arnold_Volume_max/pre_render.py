#-*- coding:utf-8 -*-

import os
import hou

hip_dir = hou.hscriptExpression('$HIP')
log_dir = hip_dir + '/script/sim_log/'


# log_dir 경로가 없을 경우 경로를 생성하고, 있을 경우 파일을 제거
if os.path.isdir(log_dir) == False:
	os.mkdir(log_dir)
else:
	if os.path.isfile(log_dir + 'density.txt'):
		os.remove(log_dir + 'density.txt')
	if os.path.isfile(log_dir + 'temperature.txt'):
		os.remove(log_dir + 'temperature.txt')
	if os.path.isfile(log_dir + 'heat.txt'):
		os.remove(log_dir + 'heat.txt')



