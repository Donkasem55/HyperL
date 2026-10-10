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
				if tmp2[0][0] == "OPERATION":
					tmparr[-1] += (tmp2)
					tmparr[-1] = [tmparr[-1]]
				else:
					tmparr[-1].append(tmp2)
			tmp2 = []
			tmparr.append([])
			tmparr2.append("PAREN")

		elif i[0] == "RPAREN":
			if tmparr2.pop(-1) == "PAREN":
				tmp = tmparr.pop(-1)
				if tmp2:
					try:
						tmparr[-1][-1].append(tmp2)
					except:
						tmparr[-1].append(tmp2)
				tmp2 = []
				if tmp:
					if tmparr[-1]:
						tmparr[-1][-1].append(tmp)
					else:
						tmparr[-1].append(tmp)

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
			if data[0] == "*":
				ret["TYPE"] = "DEREF"
				ret["NODE"] = data[1]
				return ret

			elif data[0] == "&":
				ret["TYPE"] = "ADDRESS"
				ret["NODE"] = data[1]
				return ret

			elif data[0][1] == "func":
				ret["TYPE"] = "FUNCDEF"
				ret["NODE"] = data[1][1]
				ret["LINE"] = data[0][2]
				ret["ARGS"] = []
				args = []
				ret["ARGC"] = 0
				i = 2
				e = False
				while i < len(data):
					if data[i][1] == "->" and not e:
						ret["RETTYPE"] = data[i+1][1]
						i += 1
						e = True

					elif data[i][1] == "<=":
						args.append([])
						ret["ARGC"] += 1

					else:
						args[-1].append(data[i])

					i += 1

				for j in args:
					arg = {"const":False,"readonly":False,"DATATYPE":"","local":True,"DEFAULT":0}
					i = 0
					while i < len(j):
						if j[i][1] == "int":
							arg["DATATYPE"] += "INT"
						elif j[i][1] == "unsigned":
							arg["DATATYPE"] += "UNSIGNED"
						elif j[i][1] == "long":
							arg["DATATYPE"] += "LONG"
						elif j[i][1] == "str":
							arg["DATATYPE"] += "STR"
						elif j[i][1] == "float":
							arg["DATATYPE"] += "FLOAT"
						elif j[i][1] == "double":
							arg["DATATYPE"] += "DOUBLE"
						elif j[i][1] == "pointer":
							arg["DATATYPE"] += "PTR"

						elif j[i][0] == "COLON":
							if j[i+1][1] in arg:
								arg[j[i+1][1]] = True

						elif j[i][1] == "<-":
							arg["DEFAULT"] = j[i+1][1]

						elif j[i][1] == "->":
							arg["DEFAULT"] = j[i+1][1]

						elif j[i][0] == "VARIABLE":
							arg["NAME"] = j[i][1]

						arg["DATATYPE"] = arg["DATATYPE"].replace("LONGINT", "LONG")
						arg["DATATYPE"] = arg["DATATYPE"].replace("UNSIGNEDINT", "UNSIGNED")

						i += 1

					ret["ARGS"].append(arg)

				return ret

		except:
			pass

		if type(data[0]) is tuple:
			ret = {"TYPE": "EXPR", "LINE": data[0][2]}

		else:
			ret["TYPE"] = "LIST"
			ret["LINE"] = data[0][0][2]

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
				ft = "INT"
				nb = 1
				r = 0
				a, b = ret["NODE"][0], ret["NODE"][2]
				if a["TYPE"] in ["INT", "FLOAT", "DOUBLE"] and b["TYPE"] in ["INT", "FLOAT", "DOUBLE"]:
					r = a["NODE"]
					nb = b["NODE"]

				if a["TYPE"] == "FLOAT" or b["TYPE"] == "FLOAT":
					ft = "FLOAT"
					
				if a["TYPE"] == "DOUBLE" or b["TYPE"] == "DOUBLE":
					ft = "DOUBLE"

				ret["TYPE"] = "MATH_BINARY"
				ret["OPERATION"] = t
				if t == "+":
					ret["OPERATION"] = "PLUS"
					r += nb
				elif t == "-":
					ret["OPERATION"] = "SUBTRACT"
					r -= nb
				elif t == "*":
					ret["OPERATION"] = "MULTIPLY"
					r *= nb
				elif t == "/":
					ret["OPERATION"] = "DIVIDE"
					ft = "DOUBLE"
					r /= nb
				elif t == "\\":
					ret["OPERATION"] = "INTDIV"
					r //= nb
				elif t == "&&":
					ret["OPERATION"] = "BOOLAND"
					r = r and nb
				elif t == "&":
					ret["OPERATION"] = "AND"
					r = r & nb
				elif t == "%":
					ret["OPERATION"] = "MODULO"
					r = r % nb
				elif t == "<<":
					ret["OPERATION"] = "SHL"
					r = r << nb
				elif t == ">>":
					ret["OPERATION"] = "SHR"
					r = r >> nb

				if a["TYPE"] in ["INT", "FLOAT", "DOUBLE"] and b["TYPE"] in ["INT", "FLOAT", "DOUBLE"]:
					ret = {"TYPE":ft, "NODE":r, "LINE":ret["LINE"]}

				else:
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

			elif ret["NODE"][1]["TYPE"] == "UNARY":
				t = ret["NODE"][1]["NODE"]

				ret["TYPE"] = "MATH_UNARY"
				ret["OPERATION"] = t
				if t == "+=":
					ret["OPERATION"] = "PLUS"
				elif t == "-=":
					ret["OPERATION"] = "SUBTRACT"
				elif t == "*=":
					ret["OPERATION"] = "MULTIPLY"
				elif t == "/=":
					ret["OPERATION"] = "DIVIDE"
				elif t == "\\=":
					ret["OPERATION"] = "INTDIV"
				elif t == "&=":
					ret["OPERATION"] = "AND"
				elif t == "%=":
					ret["OPERATION"] = "MODULO"
				elif t == "<<=":
					ret["OPERATION"] = "SHL"
				elif t == ">>=":
					ret["OPERATION"] = "SHR"

				ret["NODE"].pop(1)



		if ret["TYPE"] == "EXPR":
			if ret["NODE"][0]["NODE"] == "if":
				ret["TYPE"] = "IF"
				ret["NODE"] = ret["NODE"][1]

			elif ret["NODE"][0]["NODE"] == "while":
				ret["TYPE"] = "WHILE"
				ret["NODE"] = ret["NODE"][1]

			elif ret["NODE"][0]["NODE"] == "for":
				ret["TYPE"] = "FOR"
				ret["NODE"] = ret["NODE"][1]

			elif ret["NODE"][0]["TYPE"] == "KEYWORD":
				if ret["NODE"][0]["NODE"] in ["int", "float", "double", "str", "unsigned", "long", "pointer"]:
					arg = {"const":False,"readonly":False,"DATATYPE":"","local":False}
					j = ret["NODE"]
					i = 0
					while i < len(j):
						if j[i]["NODE"] == "int":
							arg["DATATYPE"] += "INT"
							arg["DEFAULT"] = 0
						elif j[i]["NODE"] == "unsigned":
							arg["DATATYPE"] += "UNSIGNED"
							arg["DEFAULT"] = 0
						elif j[i]["NODE"] == "long":
							arg["DATATYPE"] += "LONG"
							arg["DEFAULT"] = 0
						elif j[i]["NODE"] == "str":
							arg["DATATYPE"] += "STR"
						elif j[i]["NODE"] == "float":
							arg["DATATYPE"] += "FLOAT"
							arg["DEFAULT"] = 0.0
						elif j[i]["NODE"] == "double":
							arg["DATATYPE"] += "DOUBLE"
							arg["DEFAULT"] = 0.0
						elif j[i]["NODE"] == "pointer":
							arg["DATATYPE"] = "PTR"
							arg["DEFAULT"] = 0

						elif j[i]["TYPE"] == "COLON":
							if j[i+1]["NODE"] in arg:
								arg[j[i+1]["NODE"]] = True

						elif j[i]["NODE"] == "<-":
							arg["DEFAULT"] = {"TYPE":"ADDRESS", "NODE":f"{j[i+1]["NODE"]}"}
							arg["DATATYPE"] = "PTR"

						elif j[i]["NODE"] == "->":
							g = [k["NODE"] for k in j[i+1:]]
							if len(g) > 1:
								arg["DEFAULT"] = astree(g)
							else:
								arg["DEFAULT"] = j[i+1]["NODE"]

						elif j[i]["TYPE"] == "VARIABLE" and j[i-1]["TYPE"] not in ["CF", "OPERATION"]:
							arg["NAME"] = j[i]["NODE"]

						arg["DATATYPE"] = arg["DATATYPE"].replace("LONGINT", "LONG")
						arg["DATATYPE"] = arg["DATATYPE"].replace("UNSIGNEDINT", "UNSIGNED")

						i += 1

					ret["NODE"] = arg
					ret["TYPE"] = "VARDEF"

			else:
				try:
					if ret["NODE"][1]["NODE"] == "->":
						ret1, ret2 = ret["NODE"][0], ret["NODE"][2:]
						if len(ret2) > 1:
							ret2 = astree(ret2)
						ret = {"LINE":ret["LINE"]}
						ret["TYPE"] = "ASSIGNMENT"
						if ret1["TYPE"] == "FUNCTIONCALL":
							ret1 = {"TYPE":"VARIABLE", "NODE":ret1["NODE"]}
						ret["NODE"] = [ret1, ret2]
						return ret

				except IndexError:
					pass

				if ret["NODE"][0]["TYPE"] == "FUNCTIONCALL":
					try:
						args = ret["NODE"][1:]
					except IndexError:
						return ret

					ret = {"TYPE": "FUNCTIONCALL", "ARGPOS": [], "ARGNAME": {}, "NODE": ret["NODE"][0]["NODE"], "LINE": ret["LINE"]}
					i = 0
					while i < len(args):
						if args[i]["NODE"] == "<=":
							try:
								if args[i+2]["NODE"] == "->":
									ret["ARGNAME"][args[i+1]["NODE"]] = args[i+3]["NODE"]
									i += 4
								else:
									ret["ARGPOS"].append(args[i+1]["NODE"])
									i += 1
							except:
								ret["ARGPOS"].append(args[i+1]["NODE"])
								i += 1

						i += 1


	else:
		if data[0] == "FUNCTION":
			ret = {"TYPE": "FUNCTIONCALL", "ARGPOS": [], "ARGNAME": {}, "NODE": data[1], "LINE": data[2]}
		else:
			ret = {"TYPE": data[0], "NODE": data[1], "LINE": data[2]}

			if ret["TYPE"] == "KEYWORD":
				if ret["NODE"] == "do":
					ret["TYPE"] = "DO"

	return ret


def asttest(filename="test/test.hl"):
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
	ast = astree(cst)
	pprint.pp(ast, width=120, indent=4)

	print("\n\nMade by Raine (TheLuckyCuber999)\n\n") # you can delete this line if you want to, since it's public domain, but please don't :(

if __name__ == "__main__":
	asttest()
