# a function larping as a constructor
def prim(datatype, data):
	return (datatype, data)

def prim_det(data): # primitive determiner
	if data[0] == '"':
		return ("STR", data)

	elif data[0] == "'":
		return ("CHAR", data)

	elif data.isdigit():
		return ("INT", int(data))

	elif data[0] == "0":
		if data[1] == "x":
			return ("INT", int(data[2:], 16))
		elif data[1] == "b":
			return ("INT", int(data[2:], 2))
		elif data[1] == "o":
			return ("INT", int(data[2:], 8))
		elif data[1] == "-":
			if data[2] == "x":
				return ("INT", 0-int(data[3:], 16))
			elif data[2] == "b":
				return ("INT", 0-int(data[3:], 2))
			elif data[2] == "o":
				return ("INT", 0-int(data[3:], 8))
			elif data[1:].isdigit():
				return ("INT", 0-int(data[1:]))

		elif data.isdigit():
			return ("INT", int(data[1:]))
	
	ft = data.split(".") # float test
	if len(data) == 2:
		if ft[0].isdigit() and ft[1].isdigit():
			return ("DOUBLE", float(data))

		elif ft[0].isdigit() and ft[1][-1] == "f" and ft[1][:-1].isdigit():
			return ("FLOAT", float(data))

	return False
