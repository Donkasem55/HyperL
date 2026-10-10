from lexer import token, lexer
from AST import cstree, astree
import pprint

var = {}
local = [{}]
gi = 0
func = {}

def gencode(data):
	global gi, var, constvar, rovar, local
	progdata, rodata, bss, code = [], [], [], []
	if data["TYPE"] == "LIST":
		j = 0
		while j < len(data["NODE"]):
			i = data["NODE"][j]
			if i["TYPE"] == "IF":
				a, b, c, d = gencode(i["NODE"])
				progdata += a
				rodata += b
				bss += c
				code += d

				j += 1
				a, b, c, d = gencode(data["NODE"][j])
				gi += 1
				code += [["jne", ("label", f"gi{gi}")]]
				progdata += a
				rodata += b
				bss += c
				code += d
				code += [["label", f"gi{gi}"]]

			elif i["TYPE"] == "WHILE":
				a1, b1, c1, d1 = gencode(i["NODE"])

				j += 1
				a, b, c, d = gencode(data["NODE"][j])
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
				a1, b1, c1, d1 = gencode(data["NODE"][j+2]["NODE"])

				j += 1
				a, b, c, d = gencode(data["NODE"][j])
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
				args = {}
				for k in i["ARGS"]:
					args[k["NAME"]] = k

				func[i["NODE"]] = args
				code += [["label", f"_{i["NODE"]}"]]
				code += [["push", ("reg", "bp")]]
				code += [["mov ptrsize", ("reg", "bp"), ("reg", "sp")]]
				code += [["add", ("reg", "bp"), ("ptrsize_2x")]]
				l = 0
				for k in i["ARGS"]:
					e = {"TYPE":"VARDEF", "NODE":k}
					e["NODE"]["local"] = False
					d, c, ___, _ = gencode(e)
					d += c
					for b in d:
						code += [["define_allocated_local", b]]

			elif i["TYPE"] == "ASSIGNMENT":
				node = i["NODE"][0]["NODE"]
				default = i["NODE"][1]
				if i["NODE"][0]["TYPE"] == "REGISTER":
					code.append(["mov reg", f"{node}", default])
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
					code.append(["mov ptrsize", f"_{node}", {"TYPE":"ADDRESS", "NODE":f"gi{gi}"}])
				elif datatype == "PTR":
					code.append(["mov ptrsize", f"_{node}", default])

			elif i["TYPE"] == "BOOL_BINARY":
				code.append(["bool_binary_operation", i])

			else:
				a, b, c, d = gencode(i)
				progdata += a
				rodata += b
				bss += c
				code += d

			j += 1

	elif data["TYPE"] == "VARDEF":
		add = []
		datatype = data["NODE"]["DATATYPE"]
		default = data["NODE"]["DEFAULT"]

		if type(default) is dict:
			if default["TYPE"] == "ADDRESS":
				default["NODE"] = f"_{default["NODE"]}"

		elif type(default) is str:
			default = {"TYPE":"STR", "NODE":[ord(i) for i in default] + [0]}
		else:
			default = {"TYPE":datatype, "NODE":default}

		if datatype in ["INT", "UNSIGNED"]:
			add.append([2, f"_{data["NODE"]["NAME"]}", default])
		elif datatype in ["LONG", "UNSIGNEDLONG"]:
			add.append([4, f"_{data["NODE"]["NAME"]}", default])
		elif datatype in ["LONGLONG", "UNSIGNEDLONGLONG"]:
			add.append([8, f"_{data["NODE"]["NAME"]}", default])
		elif datatype == "FLOAT":
			add.append([4, f"_{data["NODE"]["NAME"]}", default])
		elif datatype == "DOUBLE":
			add.append([8, f"_{data["NODE"]["NAME"]}", default])
		elif datatype == "STR":
			gi += 1
			add.append([1, f"gi{gi}", default])
			add.append(["ptrsize", f"_{data["NODE"]["NAME"]}", {"TYPE":"ADDRESS", "NODE":f"gi{gi}"}])
		elif datatype == "PTR":
			add.append(["ptrsize", f"_{data["NODE"]["NAME"]}", default])

		if data["NODE"]["local"] == True:
			for i in add:
				code.append(["register_local", i])

		elif data["NODE"]["readonly"] == True:
			var[data["NODE"]["NAME"]] = (datatype, "RO")
			rodata += add
		elif data["NODE"]["const"] == True:
			var[data["NODE"]["NAME"]] = (datatype, "CONST")
			progdata += add
		else:
			var[data["NODE"]["NAME"]] = (datatype, "MUT")
			progdata += add

	elif data["TYPE"] == "BOOL_BINARY":
		code.append(["bool_binary_operation", data])

	return progdata, rodata, bss, code

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
	data, rodata, bss, code = gencode(AST)
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

	print("\n\nMade by Raine (TheLuckyCuber999)\n\n") # you can delete this line if you want to, since it's public domain, but please don't :(

if __name__ == "__main__":
	test()
