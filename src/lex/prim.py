# a function larping as a constructor
def prim(datatype, data):
	return (datatype, data)

def prim_det(data): # primitive determiner
	if data[0] == '"':
		return ("string", data)

	elif data[0] == "'":
		return ("char", data)

	elif data.isdigit():
		return ("int", int(data))

	elif data[0] == "0":
		if data[1] == "x":
			return ("int", int(data[2:], 16))
		elif data[1] == "b":
			return ("int", int(data[2:], 2))
		elif data[1] == "o":
			return ("int", int(data[2:], 8))
		elif data[1] == "-":
			if data[2] == "x":
				return ("int", 0-int(data[3:], 16))
			elif data[2] == "b":
				return ("int", 0-int(data[3:], 2))
			elif data[2] == "o":
				return ("int", 0-int(data[3:], 8))
			elif data[1:].isdigit():
				return ("int", 0-int(data[1:]))

		elif data.isdigit():
			return ("int", int(data[1:]))
	
	ft = data.split(".") # float test
	if len(data) == 2:
		if ft[0].isdigit() and ft[1].isdigit():
			return ("double", float(data))

		elif ft[0].isdigit() and ft[1][-1] == "f" and ft[1][:-1].isdigit():
			return ("float", float(data))

	raise TypeError(f"Unknown primitive {data} found while lexing.")
