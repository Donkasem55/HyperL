from util import *

# lexer stuff
from lex.prim import prim, prim_det
from lex.keyword import keyword
from lex.cf import cf
from lex.bl import bl
from lex.reg import reg
from lex.var import var, func

KWlist = ["func", "if", "while", "for", "do", "int", "float", "double", "str", "unsigned", "long", "const", "readonly", "pointer"] # keywords list
FNKWlist = ["func"] # function defining keywords list
CFlist = ["=>", "<=", "->", "<-"] # controlflow list
BOOLlist = ["==", "!=", "<==", ">==", "<", ">"]
PUNClist = ";,:$(){}[]"
HYPERPUNClist = "{}"
SEMICOLON = ("SEMICOLON", ";")
OPR = "+-*/&"
OPRKEY = ["+", "-", "*", "/", "&&", "&", "\\", "%", "<<", ">>"]
INSOPRKEY = ["+=", "-=", "*=", "/=", "<<=", ">>=", "\\=", "%="]

def token(data):
	ret = [""]
	clarr = [1]
	flag = [False, False, False]
	j = 0
	l = 1
	while j < len(data):
		i = data[j]
		if strifin(i, PUNClist):
			if flag[1] or flag[2]:
				pass
			elif flag[0]:
				ret[-1] += i
			else:
				ret.append(i)
				clarr.append(l)

		elif i == " ":
			if flag[1] or flag[2]:
				pass
			elif flag[0]:
				ret[-1] += i
			else:
				ret.append("")
				clarr.append(l)

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
							clarr.append(l)

					except IndexError:
						ret.append(i)
						clarr.append(l)


		elif i == "\n":
			flag[0], flag[1], = False, False
			ret.append("")
			l += 1
			clarr.append(l)

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
					clarr.append(l)
			except IndexError:
				ret.append(i)
				clarr.append(l)

		elif i == '"':
			if flag[1] or flag[2]:
				pass

			elif flag[0]:
				flag[0] = False
				ret[-1] += '"'
				ret.append("")
				clarr.append(l)

			else:
				flag[0] = True
				ret.append('"')
				clarr.append(l)

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
					clarr.append(l)
				else:
					ret[-1] += i

			except IndexError:
				ret[-1] += i

		j += 1

	k = len(ret)
	i = 0
	while i < k:
		if ret[i] == "":
			ret.pop(i)
			clarr.pop(i)
			k -= 1
			continue
		i += 1

	return (ret, clarr)

def lexer(data):
	lines = data[1]
	data = data[0]
	j = 0
	ret = [("", "")]
	ad = False
	while j < len(data):
		i = data[j]
		l = lines[j]
		t = prim_det(i)
		if t != False:
			ret.append(t + tuple([l]))
			j += 1
			continue

		if i in KWlist:
			ret.append(keyword(i) + tuple([l]))

		elif i in BOOLlist:
			ret.append(bl(i) + tuple([l]))

		elif i in CFlist:
			ret.append(cf(i) + tuple([l]))
			if i == "->" and data[j+1] not in ["*", "&"] and data[j+2] not in [";", "<="]:
				print(data[j:j+3])
				ret.append(("LPAREN", "(") + tuple([l]))
				ad = True

		elif i[0] == "%":
			if len(i) > 1:
				if i[1] == "%":
					ret.append(("OPERATION", "%", l))
				else:
					ret.append(reg(i[1:]) + tuple([l]))

		elif i in OPRKEY:
			ret.append(("OPERATION", i) + tuple([l]))

		elif i in INSOPRKEY:
			ret.append(("UNARY", i) + tuple([l]))

		elif strifin(i, PUNClist):
			if i == "(":
				ret.append(("LPAREN", i) + tuple([l]))
			elif i == ")":
				ret.append(("RPAREN", i) + tuple([l]))
			elif i == "{":
				ret.append(("LCURLB", i) + tuple([l]))
			elif i == "}":
				ret.append(("RCURLB", i) + tuple([l]))
			elif i == "[":
				ret.append(("LSQBRAC", i) + tuple([l]))
			elif i == "]":
				ret.append(("RSQBRAC", i) + tuple([l]))

			elif i == "$":
				ret.append(("DOLLAR", i) + tuple([l]))
			elif i == ":":
				ret.append(("COLON", i) + tuple([l]))
			elif i == ";":
				if ad:
					ret.append(("RPAREN", ")") + tuple([l]))
					ad = False
				ret.append(("SEMICOLON", i) + tuple([l]))
			elif i == ",":
				ret.append(("COMMA", i) + tuple([l]))

			else:
				ret.append(("PUNC", i) + tuple([l]))

		else:
			if ret[-1][0] in ["SEMICOLON"] or strifin(ret[-1][1], HYPERPUNClist) or ret[-1][1] in FNKWlist:
				ret.append(func(i) + tuple([l]))

			else:
				ret.append(var(i) + tuple([l]))

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
	for i in range(len(tok[0])):
		print(f"' {tok[0][i]} '", end="")
		if i != len(tok[0])-1:
			print(", ", end="")

	print("\n\nLexed Abstract Tokens: \n")
	lex = lexer(tok)
	for i in lex:
		print("\t", i)
	print()

if __name__ == "__main__":
	lextest()
