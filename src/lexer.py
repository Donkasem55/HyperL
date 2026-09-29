from util import *

# lexer stuff
from lex.prim import prim, prim_det
from lex.keyword import keyword
from lex.cf import cf
from lex.reg import reg
from lex.var import var, func

KWlist = ["func"] # keywords list
FNKWlist = ["func"] # function defining keywords list
CFlist = ["=>", "<=", "->", "<-"] # controlflow list
PUNClist = ";,:!$%(){}[]"
SEMICOLON = ("SEMICOLON",)


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

		elif i == "\n":
			flag[0], flag[1], = False, False
			ret.append("")

		elif strifin(i, "=><-"):
			if flag[1] or flag[2]:
				j += 1
				continue

			elif flag[0]:
				ret[-1] += i
				j += 1
				continue

			try:
				if strifin(ret[-1][-1], "=><-"):
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
				if strifin(ret[-1][-1], "=><-"):
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

		elif i in CFlist:
			ret.append(cf(i))

		elif i == ";":
			ret.append(SEMICOLON)

		elif strifin(i, PUNClist):
			ret.append(("PUNC", i))

		elif i[0] == "%":
			ret.append(reg(i[1:]))

		else:
			if ret[-1][0] in ["PUNC", "SEMICOLON"] or ret[-1][1] in FNKWlist:
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
	print(token(d))
	tok = token(d)
	print(lexer(tok))
	lex = lexer(tok)

if __name__ == "__main__":
	lextest()
