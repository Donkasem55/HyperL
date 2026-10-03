from lexer import token, lexer
from AST import cstree, astree
import pprint

var = {}
gi = 0

def gencode(data):
	global gi, var, constvar, rovar
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
		if datatype in ["INT", "UNSIGNED"]:
			add.append(["word", f"_{data["NODE"]["NAME"]}", default])
		elif datatype in ["LONG", "UNSIGNEDLONG"]:
			add.append(["dword", f"_{data["NODE"]["NAME"]}", default])
		elif datatype in ["LONGLONG", "UNSIGNEDLONGLONG"]:
			add.append(["quadword", f"_{data["NODE"]["NAME"]}", default])
		elif datatype == "FLOAT":
			add.append(["dword", f"_{data["NODE"]["NAME"]}", default])
		elif datatype == "DOUBLE":
			add.append(["quadword", f"_{data["NODE"]["NAME"]}", default])
		elif datatype == "STR":
			add.append(["byte", f"gi{gi}", [ord(i) for i in default] + [0]])
			add.append(["pointer", f"_{data["NODE"]["NAME"]}", f"gi{gi}"])
			gi += 1
		elif datatype == "PTR":
			add.append(["pointer", f"_{data["NODE"]["NAME"]}", default])

		if data["NODE"]["readonly"] == True:
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
	for i in range(len(tok)):
		print(f"' {tok[i]} '", end="")
		if i != len(tok)-1:
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
