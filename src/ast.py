from lexer import lexer

binops = ["+", "-", "*", "/", "//", "%", "==", "!=", ">==", "<=="]

uT = ["FLOAT", "INT", "DOUBLE"]

def evalexpr(data, o=[True]): # optimisation flags: ( compute number literal [operation] number literal during compile time? )
	if len(data) == 1:
		return data[0]

	if o[0] and len(data) == 3 and data[0][0] in uT and data[2][0] in uT:
		ft = "INT"
		if data[1][1] == "/":
			ft = "FLOAT"

		if data[0][0] == "FLOAT" or data[2][0] == "FLOAT":
			ft = "FLOAT"

		if data[0][0] == "DOUBLE" or data[2][0] == "DOUBLE":
			ft = "DOUBLE"

		if data[1][1] == "+":
			ret = float(data[0][1]) + float(data[2][1])

		elif data[1][1] == "-":
			ret = float(data[0][1]) - float(data[2][1])

		elif data[1][1] == "*":
			ret = float(data[0][1]) * float(data[2][1])

		elif data[1][1] == "/":
			ret = float(data[0][1]) / float(data[2][1])

		elif data[1][1] == "//":
			ret = float(data[0][1]) // float(data[2][1])

		elif data[1][1] == "%":
			ret = float(data[0][1]) % float(data[2][1])

		if data[1][1] in ["//", "%"]:
			ft = "INT"

		if ft == "FLOAT" or ft == "DOUBLE":
			return (ft, float(ret))
		elif ft == "INT":
			return (ft, int(ret))


	expr = [[], tuple(), []]
	i = 0
	lvl = 0 # level of nesting brackets

	if len(data) == 3:
		return data

	while i < len(data):
		if data[i][1] == "(":
			if lvl > 0:
				expr[0].append(data[i])
			lvl += 1

		elif lvl == 0:
			if data[0][1] != "(":
				expr[0].append(data[i])
				i += 1
			break

		elif data[i][1] == ")":
			if lvl == 0:
				break
			else:
				if lvl > 1:
					expr[0].append(data[i])

				lvl -= 1

		else:
			expr[0].append(data[i])

		i += 1

	expr[1] = data[i]
	i += 1

	j = i
	lvl = 0
	while i < len(data):
		if data[i][1] == "(":
			if lvl > 0:
				expr[2].append(data[i])
			lvl += 1

		elif lvl == 0:
			expr[2].append(data[i])
			break

		elif data[i][1] == ")":
			if lvl == 0:
				break
			else:
				if lvl > 1:
					expr[2].append(data[i])
				lvl -= 1

		else:
			expr[2].append(data[i])

		i += 1

	a = evalexpr(expr[0], o)
	b = evalexpr(expr[2], o)

	expr[0] = a
	expr[2] = b

	if len(data) > i+1:
		expr = evalexpr([expr] + data[i+1:])

	return expr



if __name__ == "__main__":
	print(evalexpr([("VARIABLE", "x"), ("OPERATION", "/"), ("DOUBLE", 4.0)]))
	print(evalexpr(lexer(["x",  "/", "(", "y", "*", "(", "5", "*", "4", ")", ")"])))
	print(evalexpr(lexer(["(", "x", "+", "5", ")",  "/", "(", "y", "*", "(", "5", "*", "4", ")", ")"])))
	print(evalexpr(lexer(["x", "+", "5",  "/", "(", "y", "*", "(", "5", "*", "4", ")", ")"])))
	print(evalexpr([('VARIABLE', 'y'), ('OPERATION', '*'), ('PUNC', '('), ('INT', 5), ('OPERATION', '*'), ('INT', 4), ('PUNC', ')')]))
	print(evalexpr([("FLOAT", 5.0), ("OPERATION", "/"), ("DOUBLE", 4.0)]))
