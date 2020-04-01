
hou.hipFile.load(file_name='/home/gulliver/Desktop/Job/Study/command_line/test_v01.hip')


hip_dir = hou.hscriptExpression('$HIP')

new_geo = hou.node('/obj').createNode('geo')


font_node = new_geo.createNode('font')

font_node.parm('text').set(hip_dir)

print(hou.isUIAvailable(1))

#print(hou.ui.paneTabs())


hou.hipFile.save(file_name='/home/gulliver/Desktop/Job/Study/command_line/test_v02.hip')
#
# print(hip_dir)
# #ver = 'v' + str(hou.hscriptExpression('$VER').zfill(2))
# ver = 'v01'
# #wipver = str(hou.hscriptExpression('$WIPVER').zfill(2))
# wipver = 'w01'
# #justin = hou.hscriptFloatExpression('$JUSTIN')
# #justout = hou.hscriptFloatExpression('$JUSTOUT')
#
# panes = hou.ui.paneTabs()
#
# sceneview = None
#
# for i in panes:
#     if 'Scene' in str(i.type()):
#         sceneview = i
#     else:
#         pass
#
# flipbook_setup = sceneview.flipbookSettings()
#
# flipbook_setup.frameRange((1, 50))
# # flipbook_setup.resolution((1920,1080))
# flipbook_setup.useResolution(0)
#
# flipbook_setup.output(hip_dir + '/flipbook/' + ver + '_' + wipver + '/' + 'test_$F4.png')
# flipbook_setup.outputToMPlay(0)
#
# sceneview.flipbook()

