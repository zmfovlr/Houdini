# Name: Oncreated.py

manager_color = (0, 0.533, 0)	# green
generator_color = (1, 0.9, 0.65)	# ivory

# Common node type colors.	These colors affect these types in all contexts.
# Node names are matched identically with keys.

common_type_colors = {
	
	"null": (0, 0, 0), # black
	"switch": (1, 0.4, 1),	# pink
	"attribvop": (0.188, 0.529, 0.459),	# blue green
	"volumevop": (0.188, 0.529, 0.459), # blue green
	"attribwrangle": (0.1, 0.37, 0.7), # blue
	"volumewrangle": (0.1, 0.37, 0.7), # blue
}
# Specific/general node type colors based on context. By default, node names are matched
# by a search result. "hlight", "indirectlight", etc will all be matched to "light". To
# match identically, change the last argument to the checkDicionaryForTypeName() call
# to False
node_type_colors = {
	
	"object": {

		"null": (0, 0.4, 1), # blue
		"geo": (0.8, 0.8, 0.8), # gray
		"light": (1, 0.8, 0), # yellow
		"ambient": (1, 0.8, 0), # yellow
		"cam": (0.6, 0.8, 1), # skyblue
		"bone": (0.867, 0, 0), # red
	},

	"dop": {

	},
}

# Specific tab menu folders based on context. For example, all the nodes who
# ars located in the "Forces" tab in a DOP context will be colored orange.
tool_menu_colors = {
	
	"dop": {
		"Solvers": (0, 0.3, 1), # blue
		"Objects": (0.4, 1, 0.4), # green
		"Forces": (1, 0.4, 0), # orange
	},

	"sop": {
		"Manipulate": (1, 0.8, 0), # yellow
		"Import": (0.573, 0.353, 0), # brown
	},

	"vop": {
		"Geometry": (0.4, 1, 0.4), # green
		"Utility": (1, 0.4, 0), # orange
	},
}

def getNodeTypeTool(node_type):
	""" Get the hou.Tool entry for a particular node type. """
	tools = hou.shelves.tools()
	tool_name = "%s_%s" % (node_type.category().name().lower(), node_type.name())
	return	tools.get(tool_name)

def checkDicionaryForTypeName(type_dictionary, type_name, soft_check=True):
	""" Check a dictionary for a specific node type name.

		soft_check: Use a soft check by searching for the specified type
					name in the string rather than an absolute string
					match.	This allows generic names like 'light' to
					encompass several nodes at once.
	"""
	if soft_check:
		for key, color in type_dictionary.iteritems():
			if type_name.find(key) != -1:
				return color
		return	None
	else:
		# Try for a direct match of the type name.
		return type_dictionary.get(type_name)

# Node type information
node = kwargs["node"]
node_type = node.type()
node_type_name = node_type.name()
type_category_name = node_type.category().name().lower()

#  Start with no node color:
node_color = None

# Manager nodes (sopnet, chopnet, ropnet, etc).
if node_type.isManager():
	node_color = manager_color

# Common node types (nulls, switches, etc) are colored the same across
# different contexts.
elif node_type_name in common_type_colors:
	node_color = common_type_colors[node_type_name]

else:
	# Get the color mappings for this context.
	type_colors = node_type_colors.get(type_category_name)

	if type_colors is not None:
		# Check to see if there ars any mappings for this type.
		node_color = checkDicionaryForTypeName(type_colors, node_type_name, True)

	# If there were no mappings for the specific type, check for the tab
	# menu.
	if node_color is None:
		# Get the tool for the node type.
		tool = getNodeTypeTool(node_type)

		# Get a tuple of possible tab menu locations this tool will appear.
		try:
			menu_locations = tool.toolMenuLocations()
		except AttributeError:
			pass

		# Get any possible colored menu locations for this context.
		menu_colors = tool_menu_colors.get(type_category_name)

		if menu_colors is not None:
			# Iterate over all the possible locations for the tool.
			try:
				for location in menu_locations:
					# Try and get the color of the location.
					node_color = menu_colors.get(location)
					# If we got a color then use it.
					if node_color is not None:
						break
			except NameError:
				pass

	# If there have been no previous assignments, color generator nodes.
	if node_color is None and node_type.isGenerator():
		node_color = generator_color

# If we found a color mapping, set the color of the node.
if node_color is not None:
	node.setColor(hou.Color(node_color))