from lexer import token, lexer
from AST import cstree, astree
import pprint

var = {}
local = []
localoffset = []
gi = 0
func = {}

def gencode(data, ptrsize):
	global gi, var, constvar, rovar, local
	progdata, rodata, bss, code = [], [], [], []
	if data["TYPE"] == "LIST":
		j = 0
		while j < len(data["NODE"]):
			i = data["NODE"][j]
			if i["TYPE"] == "IF":
				a, b, c, d = gencode(i["NODE"], ptrsize)
				progdata += a
				rodata += b
				bss += c
				code += d

				j += 1
				a, b, c, d = gencode(data["NODE"][j], ptrsize)
				gi += 1
				code += [["jne", ("label", f"gi{gi}")]]
				progdata += a
				rodata += b
				bss += c
				code += d
				code += [["label", f"gi{gi}"]]

			elif i["TYPE"] == "WHILE":
				a1, b1, c1, d1 = gencode(i["NODE"], ptrsize)

				j += 1
				a, b, c, d = gencode(data["NODE"][j], ptrsize)
				gi += 1
				code += [["label", f"gi{gi}"]]
				progdata += a1
				rodata += b1
				bss += c1
				code += d1
				code += [["jne", ("label", f"gi{gi+1}")]]
				progdata += a
				rodata += b
				bss += c
				code += d
				code += [["jmp", ("label", f"gi{gi}")]]
				gi += 1
				code += [["label", f"gi{gi}"]]

			elif i["TYPE"] == "DO":
				a1, b1, c1, d1 = gencode(data["NODE"][j+2]["NODE"], ptrsize)

				j += 1
				a, b, c, d = gencode(data["NODE"][j], ptrsize)
				gi += 1
				code += [["label", f"gi{gi}"]]
				progdata += a
				rodata += b
				bss += c
				code += d
				progdata += a1
				rodata += b1
				bss += c1
				code += d1
				code += [["je", ("label", f"gi{gi}")]]
				j += 1

			elif i["TYPE"] == "FUNCDEF":
				local.append(dict())
				localoffset.append(dict())
				args = {}
				argsoffset = 0
				for k in i["ARGS"]:
					args[k["NAME"]] = k
				func[i["NODE"]] = args

				for k in args:
					datatype = args[k]["DATATYPE"]
					default = args[k]["DEFAULT"]
					if datatype in ["INT", "UNSIGNED"]:
						datatype = 2
					elif datatype in ["LONG", "UNSIGNEDLONG"]:
						datatype = 4
					elif datatype in ["LONGLONG", "UNSIGNEDLONGLONG"]:
						datatype = 8
					elif datatype == "FLOAT":
						datatype = 4
					elif datatype == "DOUBLE":
						datatype = 8
					elif datatype == "STR":
						gi += 1
						progdata += [[1, f"gi{gi}", default]]
						datatype = ptrsize
						default = {"TYPE":"ADDRESS", "NODE":f"gi{gi}"}
					elif datatype == "PTR":
						datatype = ptrsize
					args[k]["DATATYPE"] = datatype
					args[k]["DEFAULT"] = default
					func[i["NODE"]][k] = args
					args[k] = (datatype, default)

				for k in args:
					local[-1][k] = args[k]
					for m in localoffset[-1]:
						localoffset[-1][m][0] += args[k][0]
					localoffset[-1][k] = [0, args[k][1]]
					argsoffset += args[k][0]
				j += 1
				a, b, c, d = gencode(data["NODE"][j], ptrsize)
				offset = 0
				for k in local[-1]:
					for m in localoffset[-1]:
						localoffset[-1][m][0] += local[-1][k][0]
					localoffset[-1][k] = [0, local[-1][k][1]]
					offset += local[-1][k][0]

				code += [["label", f"_{i["NODE"]}"]]
				code += [[f"mov {ptrsize}", "TEMP", ("reg", "r1")]]
				code += [["pull reg", ("reg", "r1")]]
				code += [["add reg", ("reg", "sp"), {"TYPE":"INT", "NODE":argsoffset+2*ptrsize}]]
				code += [["push reg", ("reg", "r1")]]
				code += [["push reg", ("reg", "bp")]]
				code += [["sub reg", ("reg", "sp"), {"TYPE":"INT", "NODE":offset}]]
				code += [["mov reg", ("reg", "bp"), ("reg", "sp")]]

				for k in local[-1]:
					if k not in args:
						code += [["mov reg", ("reg", "r1"), local[-1][k][2]]]
						code += [[f"mov {local[-1][k][0]}", ("offset", "bp", localoffset[-1][k][0]), ("reg", "r1")]]

				code += [["mov reg", ("reg", "r1"), "TEMP"]]
				l = 0
				progdata += a
				rodata += b
				bss += c
				code += d
				code += [["add reg", ("reg", "sp"), {"TYPE":"INT", "NODE":offset}]]
				code += [["pull reg", ("reg", "bp")]]
				code += [["ret"]]
				local.pop(-1)
				localoffset.pop(-1)

			elif i["TYPE"] == "FUNCTIONCALL":
				args = func[i["NODE"]]

				arg = {k:[] for k in args}
				for k in args:
					if k in i["ARGS"]:
						if i["ARGS"][k]["TYPE"] in ["INT", "FLOAT", "DOUBLE"]:
							arg[k] = [[f"push {args[k][0]}", i["ARGS"][k]["NODE"]]]
						elif i["ARGS"][k]["TYPE"] == "STR":
							gi += 1
							progdata += [[1, f"gi{gi}", i["ARGS"][k]["NODE"]]]
							arg[k] = [[f"push {ptrsize}", {"TYPE":"ADDRESS", "NODE":f"gi{gi}"}]]

					else:
						arg[k] = [[f"push {args[k][0]}", args[k][1]]]

				for k in arg:
					code += arg[k]

			elif i["TYPE"] == "ASSIGNMENT":
				node = i["NODE"][0]["NODE"]
				default = i["NODE"][1]
				if i["NODE"][0]["TYPE"] == "REGISTER":
					code.append(["mov reg_abs", ("reg_abs", f"{node}"), default])
					j += 1
					continue
				datatype = var[i["NODE"][0]["NODE"]][0]
				if datatype in ["INT", "UNSIGNED"]:
					code.append(["mov 2", f"_{node}", default])
				elif datatype in ["LONG", "UNSIGNEDLONG"]:
					code.append(["mov 4", f"_{node}", default])
				elif datatype in ["LONGLONG", "UNSIGNEDLONGLONG"]:
					code.append(["mov 8", f"_{node}", default])
				elif datatype == "FLOAT":
					code.append(["mov 4", f"_{node}", default])
				elif datatype == "DOUBLE":
					code.append(["mov 8", f"_{node}", default])
				elif datatype == "STR":
					gi += 1
					progdata.append([1, f"gi{gi}", default])
					code.append([f"mov {ptrsize}", f"_{node}", {"TYPE":"ADDRESS", "NODE":f"gi{gi}"}])
				elif datatype == "PTR":
					code.append([f"mov {ptrsize}", f"_{node}", default])

			else:
				a, b, c, d = gencode(i, ptrsize)
				progdata += a
				rodata += b
				bss += c
				code += d

			j += 1

	elif data["TYPE"] == "VARDEF":
		add = []
		datatype = data["NODE"]["DATATYPE"]
		default = data["NODE"]["DEFAULT"]
		deref = False

		if type(default) is dict:
			if default["TYPE"] == "ADDRESS":
				default["NODE"] = f"_{default["NODE"]}"
			elif default["TYPE"] == "DEREF":
				deref = True

		elif type(default) is str:
			default = {"TYPE":"STR", "NODE":[ord(i) for i in default] + [0]}
		else:
			default = {"TYPE":datatype, "NODE":default}

		if datatype in ["INT", "UNSIGNED"]:
			datatype = 2
			add.append([2, f"_{data["NODE"]["NAME"]}", default])
		elif datatype in ["LONG", "UNSIGNEDLONG"]:
			datatype = 4
			add.append([4, f"_{data["NODE"]["NAME"]}", default])
		elif datatype in ["LONGLONG", "UNSIGNEDLONGLONG"]:
			datatype = 8
			add.append([8, f"_{data["NODE"]["NAME"]}", default])
		elif datatype == "FLOAT":
			datatype = 4
			add.append([4, f"_{data["NODE"]["NAME"]}", default])
		elif datatype == "DOUBLE":
			datatype = 8
			add.append([8, f"_{data["NODE"]["NAME"]}", default])
		elif datatype == "STR":
			datatype = ptrsize
			gi += 1
			add.append([1, f"gi{gi}", default])
			add.append([ptrsize, f"_{data["NODE"]["NAME"]}", {"TYPE":"ADDRESS", "NODE":f"gi{gi}"}])
		elif datatype == "PTR":
			datatype = ptrsize
			add.append([ptrsize, f"_{data["NODE"]["NAME"]}", default])

		if data["NODE"]["local"] == True:
			for i in add:
				local[-1][i[1]] = (datatype, default["NODE"], default)

		elif data["NODE"]["readonly"] == True:
			var[data["NODE"]["NAME"]] = (datatype, "RO")
			rodata += add
		elif data["NODE"]["const"] == True:
			var[data["NODE"]["NAME"]] = (datatype, "CONST")
			progdata += add
		else:
			var[data["NODE"]["NAME"]] = (datatype, "MUT")
			progdata += add

		if deref and not data["NODE"]["local"]:
			code += [[f"mov {datatype}", f"_{data["NODE"]["NAME"]}", default]]


	elif data["TYPE"] == "BOOL_BINARY":
		code.append(["bool_binary_operation", data])

	elif data["TYPE"] == "MATH_BINARY":
		code.append(["math_binary_operation", data])

	elif data["TYPE"] == "MATH_UNARY":
		code.append(["math_unary_operation", data])

		t = data["OPERATION"]
		a = data["NODE"][0]
		b = data["NODE"][1]
		if a["TYPE"] == "REGISTER":
			c = ("reg_abs", a["NODE"])
		if b["TYPE"] == "REGISTER":
			d = ("reg_abs", b["NODE"])
		if t == "PLUS":
			if a["TYPE"] == "REGISTER":
				code += [["add reg_abs", ("reg", a["NODE"])]]

	return progdata, rodata, bss, code

def compiler(ast, ptrsize):
	a, b, c, d = gencode(ast, ptrsize)
	a.append([ptrsize, "TEMP", {"TYPE":"INT", "NODE":0}])
	return a, b, c, d

def test(filename="test/test.hl"):
	# the AST tester
	with open(filename) as f:
		d = f.read()
	print("\nRaw Tokens: \n")
	tok = token(d)
	for i in range(len(tok[0])):
		print(f"' {tok[0][i]} '", end="")
		if i != len(tok[0])-1:
			print(", ", end="")

	print("\n\nLexed Tokens: \n")
	lex = lexer(tok)
	for i in lex:
		print("\t", i)

	print("\n\nConcrete Syntax Tree: \n")
	cst = cstree(lex)
	pprint.pp(cst, width=120, indent=8)

	print("\n\nAbstract Syntax Tree: \n")
	AST = astree(cst)
	pprint.pp(AST, width=120, indent=4)

	print("\n\nGenerated Procedural Intermediate Representation:")
	data, rodata, bss, code = compiler(AST, 8)
	print("\n.data:")
	for i in data:
		print("    ", i)
	print("\n.rodata:")
	for i in rodata:
		print("    ", i)
	print("\n.bss:")
	for i in bss:
		print("    ", i)
	print("\n.text:")
	for i in code:
		print("    ", i)

	print(local)

	print("\n\nMade by Raine (TheLuckyCuber999)\n\n") # you can delete this line if you want to, since it's public domain, but please don't :(

if __name__ == "__main__":
	test()
