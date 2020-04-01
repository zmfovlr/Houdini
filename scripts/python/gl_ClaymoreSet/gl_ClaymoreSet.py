#-*- coding:utf-8 -*-


import hou
import os
import math
from pprint import pprint
from itertools import product
from decimal import Decimal

menu_list = []


# 파라미터에 입력된 Wedge 값들을 얻어오는 함수
def get():
    global menu_list
    node = hou.pwd()
    parm = 'wedge_parm'
    node.parm('wedge_select').set(0)

    wedge_parms = node.parm(parm).multiParmInstances()

    value_list = []

    for i in wedge_parms:
        value_list.append(i.eval())

    dl = divide_list(value_list, 0, len(value_list), 6)

    wedge_val_list = []


    for j in dl:
        # Use Set Value가 켜져있는지 체크
        if j[4] == 0:
            # 상승값이 0일 경우 첫번째 Parm의 값으로 리스트 구성
            if j[3] == 0:
                wedge_val_list.append([j[1], j[1], j[1]])
            else:
                wedge_val_list.append(increase(j[1], j[2], j[3]))

        else:
            custom_list = j[-1].split(' ')
            set_val = []
            for c in custom_list:
                set_val.append(float(c))
            wedge_val_list.append(set_val)


    noc_list = list(product(*wedge_val_list))

    for i, n in enumerate(noc_list):
        noc_list[i] = list(n)



    wirte_wedge_val(node, len(noc_list), noc_list)

    menu_list = wedge_select_list(len(noc_list))



# 최종적으로 현재씬에 적용할 Wedge 값을 불러오는 함수
def import_btn():
    node = hou.pwd()
    parm = node.parm('wedge_select')
    parm_val = parm.eval()
    load_value = node.parm('wedge_list').eval().split('\n')

    value_list = []

    wedge_parms = node.parm('wedge_parm').multiParmInstances()

    for i in wedge_parms:
        if 'chs' in i.rawValue():
            value_list.append(i.rawValue()[6:-3])
        else:
            pass


    import_value_list = []

    for l in load_value:
        import_value_list.append(l.split(' - ')[-1])

    import_value = import_value_list[parm_val][1:-1]

    import_parm = node.parm('import_value')
    import_parm.lock(False)
    import_parm.set(import_value)
    import_parm.lock(True)

    set_value = import_value_list[parm_val][1:-1].split(', ')

    for v, s in zip(value_list, set_value):
        hou.parm(v).set(float(s))





# Wedge에 대한 값들을 Text로 출력해주는 함수
def wirte_wedge_val(node, wedge_count, noc):
    text = ''
    for i, n in zip(range(wedge_count), noc):
        text = text + 'WEDGE ' + str(i) + ' - ' + str(n) + '\n'

    list_parm = node.parm('wedge_list')
    list_parm.lock(False)
    list_parm.set(text)
    list_parm.lock(True)

    total_parm = node.parm('total_count')
    total_parm.lock(False)
    total_parm.set(str(wedge_count))
    total_parm.lock(True)



def wedge_select_list(wedge_count):
    result_list = []
    for i in range(wedge_count):
        result_list.append('{}'.format(i))
        result_list.append('WEDGE {}'.format(i))

    return result_list



# 기능 구현만 해두고 사용하지 않은 함수임
# Wedge 경우의 수에 따른 파라미터 생성
def add_parm(node):
    ptg = node.parmTemplateGroup()

    if ptg.parmTemplates()[-1].name() == 'wedge_list':
        for i in ptg.parmTemplates()[-1].parmTemplates():
            node.parm(i.name()).set(10)
    else:
        parm_folder = hou.FolderParmTemplate('wedge_list', 'Wedge List')
        parm_folder.setFolderType(hou.folderType.Simple)
        parm_folder.addParmTemplate(hou.FloatParmTemplate('first', 'First', 1))
        parm_folder.addParmTemplate(hou.FloatParmTemplate('last', 'Last', 1))
        ptg.append(parm_folder)

    node.setParmTemplateGroup(ptg)



# 리스트를 특정 갯수로 나누는 함수
def divide_list(source_list, start_pos, end_pos, div):
    div_list = []

    for i in range(start_pos, end_pos + div, div):
        out = source_list[start_pos:start_pos + div]
        if out != []:
            div_list.append(out)
        start_pos = start_pos + div

    return div_list



# 주어진 숫자가 상승되는 리스트
def increase(val0, val1, val2):
    list = [val0, val1, val2]
    icnt = list[0]
    val_list = []
    while (icnt <= list[1]):
        icnt += list[-1]
        val_list.append(float(str(icnt - list[-1])))    # 부동소수점 제거를 위해 float을 str로 변환하고 다시 float으로 변환
    return val_list
