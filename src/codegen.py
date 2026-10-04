from lexer import token, lexer
from AST import cstree, astree
import pprint

var = {}
local = [{}]
gi = 0

def gencode(data):
	global gi, var, constvar, rovar, local
	progdata, rodata, bss, code = [], [], [], []
	if data["TYPE"] == "LIST":
		for i in data["NODE"]:
			a, b, c, d = gencode(i)
			progdata += a
			rodata += b
			bss += c
			code += d

	elif data["TYPE"] == "VARDEF":
		add = []
		datatype = data["NODE"]["DATATYPE"]
		default = data["NODE"]["DEFAULT"]
		deref = False
		if type(default) is dict:
			if default["TYPE"] == "DEREF":
				default = 0
				if data["local"]:
					deref = True
				else:
					code.append(["lea", ("var",  f"_{data["NODE"]["NAME"]}"), ("var", f"_{default["NODE"]}")])
.
			elif default["TYPE"] == "ADDRESS":
				default = f"_{default["NODE"]}"

		if datatype in ["INT", "UNSIGNED"]:
			add.append([2, f"_{data["NODE"]["NAME"]}", [default]])
		elif datatype in ["LONG", "UNSIGNEDLONG"]:
			add.append([4, f"_{data["NODE"]["NAME"]}", [default]])
		elif datatype in ["LONGLONG", "UNSIGNEDLONGLONG"]:
			add.append([8, f"_{data["NODE"]["NAME"]}", [default]])
		elif datatype == "FLOAT":
			add.append([4, f"_{data["NODE"]["NAME"]}", [default]])
		elif datatype == "DOUBLE":
			add.append([8, f"_{data["NODE"]["NAME"]}", [default]])
		elif datatype == "STR":
			add.append([1, f"gi{gi}", [ord(i) for i in default] + [0]])
			add.append(["ptrsize", f"_{data["NODE"]["NAME"]}", [f"gi{gi}"]])
			gi += 1
		elif datatype == "PTR":
			add.append(["ptrsize", f"_{data["NODE"]["NAME"]}", [default]])

		if data["NODE"]["local"] == True:
			code.append(["sub", ("reg", "ptr_stack"), ("val", add[0])])

			if add[0] == "ptrsize":
				for i in local[-1]:
					local[-1][i][1][1] -= 1
			else:
				for j in add:
					for i in local[-1]:
						local[-1][i][1][0] -= j[0]
			j = 0
			for i in range(len(add)):
				if add[i][0] == "ptrsize":
					if deref:
						code.append(["lea", ("mem_stack", "+", 0), f"_{default["NODE"]}"])
					else:
						code.append(["mov ptrsize", ("mem_stack", "+", 0), ("val", default)])
					local[-1][data["NODE"]["NAME"]] = ["ptrsize", [0, 0], data["NODE"]["readonly"] or data["NODE"]["const"]]
					code.append(["register_local", f"_{data["NODE"]["NAME"]}", "ptrsize"])
				else:
					for k in add[i][2]:
						code.append([f"mov {add[i][0]}", ("mem_stack", "+", j), ("val", k)])
						code.append(["register_local", f"_{data["NODE"]["NAME"]}", add[i][0]])
						local[-1][add[i][1]] = [add[i][0], [j, 0], data["NODE"]["readonly"] or data["NODE"]["const"]]
						j += add[i][0]

		elif data["NODE"]["readonly"] == True:
			var[data["NODE"]["NAME"]] = (datatype, "RO")
			rodata += add
		elif data["NODE"]["const"] == True:
			var[data["NODE"]["NAME"]] = (datatype, "CONST")
			progdata += add
		else:
			var[data["NODE"]["NAME"]] = (datatype, "MUT")
			progdata += add

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
