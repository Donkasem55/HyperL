from util import *
from lexer import *
from const import *
from evalexpr import *

import pprint

def cstree(data):
	tmparr = [[]]
	tmparr2 = ["CURL"]
	tmp2 = []
	for j in range(len(data)):
		i = data[j]
		if i[0] == "LPAREN":
			if tmp2:
				tmparr[-1].append(tmp2)
			tmp2 = []
			tmparr.append([])
			tmparr2.append("PAREN")

		elif i[0] == "RPAREN":
			if tmparr2.pop(-1) == "PAREN":
				tmp = tmparr.pop(-1)
				if tmp2:
					tmparr[-1][-1].append(tmp2)
				tmp2 = []
				if tmp:
					tmparr[-1][-1].append(tmp)

		elif i[0] == "LCURLB":
			if tmp2:
				tmparr[-1].append(tmp2)
			tmp2 = []
			tmparr.append([])
			tmparr2.append("CURL")

		elif i[0] == "RCURLB":
			if tmparr2.pop(-1) == "CURL":
				tmp = tmparr.pop(-1)
				if tmp2:
					tmparr[-1][-1].append(tmp2)
				tmp2 = []
				if tmp:
					tmparr[-1].append(tmp)

		elif i[0] == "SEMICOLON":
			if tmp2:
				tmparr[-1].append(tmp2)
			tmp2 = []

		else:
			tmp2.append(i)

	return tmparr[0]

def astree(data):
	ret = {}
	if type(data) is list:
		try:
			if data[0][1] == "func":
				ret["TYPE"] = "FUNCDEF"
				ret["NODE"] = data[1][1]
				ret["ARGC"] = data[5][1]
				return ret

		except:
			pass

		if type(data[0]) is tuple:
			ret = {"TYPE": "EXPR"}

		else:
			ret["TYPE"] = "LIST"

		ret["NODE"] = []
		for j in range(len(data)):
			i = data[j]
			e = astree(i)
			ret["NODE"].append(e)

		if len(ret["NODE"]) == 1:
			return ret["NODE"][0]
		else:
			if ret["NODE"][1]["TYPE"] == "OPERATION":
				t = ret["NODE"][1]["NODE"]

				ret["TYPE"] = "MATH_BINARY"
				ret["OPERATION"] = t
				if t == "+":
					ret["OPERATION"] = "PLUS"
				elif t == "-":
					ret["OPERATION"] = "SUBTRACT"
				elif t == "*":
					ret["OPERATION"] = "MULTIPLY"
				elif t == "/":
					ret["OPERATION"] = "DIVIDE"
				elif t == "//":
					ret["OPERATION"] = "INTDIV"
				elif t == "&&":
					ret["OPERATION"] = "BOOLAND"
				elif t == "&":
					ret["OPERATION"] = "AND"
				elif t == "%":
					ret["OPERATION"] = "MODULO"

				ret["NODE"].pop(1)

			elif ret["NODE"][1]["TYPE"] == "BOOL":
				t = ret["NODE"][1]["NODE"]

				ret["TYPE"] = "BOOL_BINARY"
				ret["OPERATION"] = t
				if t == "<==":
					ret["OPERATION"] = "LESS_EQ"
				elif t == ">==":
					ret["OPERATION"] = "GREATER_EQ"
				elif t == "==":
					ret["OPERATION"] = "EQUAL"
				elif t == "!=":
					ret["OPERATION"] = "NEQUAL"
				elif t == "<":
					ret["OPERATION"] = "LESS"
				elif t == ">":
					ret["OPERATION"] = "GREATER"

				ret["NODE"].pop(1)

		if ret["TYPE"] == "EXPR":
			if ret["NODE"][0] == {"TYPE": "KEYWORD", "NODE": "if"}:
				ret["TYPE"] = "IF"
				ret["NODE"] = ret["NODE"][1]

			elif ret["NODE"][0] == {"TYPE": "KEYWORD", "NODE": "while"}:
				ret["TYPE"] = "WHILE"
				ret["NODE"] = ret["NODE"][1]

	else:
		ret = {"TYPE": data[0], "NODE": data[1]}

	return ret


def asttest(filename="test/test.hl"):
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
	ast = astree(cst)
	pprint.pp(ast, width=120, indent=4)

	print("\n\nMade by Raine (TheLuckyCuber999)\n\n") # you can delete this line if you want to, since it's public domain, but please don't :(

if __name__ == "__main__":
	asttest()
