from util import *

# lexer stuff
from lex.prim import prim, prim_det
from lex.keyword import keyword
from lex.cf import cf
from lex.bl import bl
from lex.reg import reg
from lex.var import var, func

KWlist = ["func", "if", "while"] # keywords list
FNKWlist = ["func"] # function defining keywords list
CFlist = ["=>", "<=", "->", "<-"] # controlflow list
BOOLlist = ["==", "!=", "<==", ">==", "<", ">"]
PUNClist = ";,:$(){}[]"
HYPERPUNClist = "{}"
SEMICOLON = ("SEMICOLON", ";")
OPR = "+-*/&"
OPRKEY = ["+", "-", "*", "/", "&&", "&", "+=", "-=", "*=", "/=", "//", "%", "<<=", ">>=", "//=", "%=", "<<", ">>"]

def token(data):
	ret = [""]
	flag = [False, False, False]
	j = 0
	while j < len(data):
		i = data[j]
		if strifin(i, PUNClist):
			if flag[1] or flag[2]:
				pass
			elif flag[0]:
				ret[-1] += i
			else:
				ret.append(i)

		elif i == " ":
			if flag[1] or flag[2]:
				pass
			elif flag[0]:
				ret[-1] += i
			else:
				ret.append("")

		elif i == "/":
			if flag[0]:
				ret[-1] += i

			elif flag[1]:
				pass

			elif flag[2]:
				if data[j-1] == "*":
					flag[2] == False

			else:
				if data[j+1] == "/":
					flag[1] = True

				elif data[j+1] == "*":
					flag[2] = True

				else:
					try:
						if strifin(ret[-1][-1], "=><-" + OPR + PUNClist):
							ret[-1] += i
						else:
							ret.append(i)

					except IndexError:
						ret.append(i)


		elif i == "\n":
			flag[0], flag[1], = False, False
			ret.append("")

		elif strifin(i, "=><-!" + OPR + PUNClist):
			if flag[1] or flag[2]:
				j += 1
				continue

			elif flag[0]:
				ret[-1] += i
				j += 1
				continue

			try:
				if strifin(ret[-1][-1], "=><-!" + OPR + PUNClist):
					ret[-1] += i
				else:
					ret.append(i)
			except IndexError:
				ret.append(i)

		elif i == '"':
			if flag[1] or flag[2]:
				pass

			elif flag[0]:
				flag[0] = False
				ret[-1] += '"'
				ret.append("")

			else:
				flag[0] = True
				ret.append('"')

		elif i == "\t":
			if flag[0]:
				ret[-1] += "\t"

		else:
			if flag[1] or flag[2]:
				j += 1
				continue

			elif flag[0]:
				ret[-1] += i
				j += 1
				continue

			try:
				if strifin(ret[-1][-1], "=><-" + OPR + PUNClist):
					ret.append(i)
				else:
					ret[-1] += i

			except IndexError:
				ret[-1] += i

		j += 1
	
	while "" in ret:
		ret.remove("")

	return ret

def lexer(data):
	j = 0
	ret = [("", "")]
	while j < len(data):
		i = data[j]
		t = prim_det(i)
		if t != False:
			ret.append(t)
			j += 1
			continue

		if i in KWlist:
			ret.append(keyword(i))

		elif i in BOOLlist:
			ret.append(bl(i))

		elif i in CFlist:
			ret.append(cf(i))

		elif i[0] == "%":
			if len(i) > 1:
				if i[1] == "%":
					ret.append(("OPERATION", "%"))
				else:
					ret.append(reg(i[1:]))

		elif i in OPRKEY:
			ret.append(("OPERATION", i))

		elif strifin(i, PUNClist):
			if i == "(":
				ret.append(("LPAREN", i))
			elif i == ")":
				ret.append(("RPAREN", i))
			elif i == "{":
				ret.append(("LCURLB", i))
			elif i == "}":
				ret.append(("RCURLB", i))
			elif i == "[":
				ret.append(("LSQBRAC", i))
			elif i == "]":
				ret.append(("RSQBRAC", i))

			elif i == "$":
				ret.append(("DOLLAR", i))
			elif i == ":":
				ret.append(("COLON", i))
			elif i == ";":
				ret.append(("SEMICOLON", i))
			elif i == ",":
				ret.append(("COMMA", i))

			else:
				ret.append(("PUNC", i))

		else:
			if ret[-1][0] in ["SEMICOLON"] or strifin(ret[-1][1], HYPERPUNClist) or ret[-1][1] in FNKWlist:
				ret.append(func(i))

			else:
				ret.append(var(i))

		j += 1

	ret.pop(0)

	return ret



#############################################
##### This is for testing purposes only #####
#############################################


def lextest(filename="test/test.hl"):
	with open(filename) as f:
		d = f.read()
	print("\nTokenised Array: \n")
	tok = token(d)
	for i in range(len(tok)):
		print(f"' {tok[i]} '", end="")
		if i != len(tok)-1:
			print(", ", end="")

	print("\n\nLexed Abstract Tokens: \n")
	lex = lexer(tok)
	for i in lex:
		print("\t", i)
	print()

if __name__ == "__main__":
	lextest()
