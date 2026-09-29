from util import *
from lexer import *
from const import *
from evalexpr import *

def tree(data):
	ls = [[]]
	i = 0
	l = 0
	l1 = 0
	tmp = []
	while i < len(data):
		if data[i][1] == "}":
			if l == 1:
				ls.append([])
				l -= 1
			else:
				l -= 1
				ls[-1].append(data[i])

		elif data[i][1] == "{":
			if l != 0:
				ls[-1].append(data[i])
			else:
				ls.append([])
			l += 1

		elif data[i][1] == "(":
			l1 += 1
			if l1 > 1:
				tmp.append(data[i])

		elif data[i][1] == ")":
			l1 -= 1
			if l1 == 0:
				ls[-1].append(evalexpr(tmp))
				tmp = []
				ls[-1].append(("SEMICOLON", ";"))
			else:
				tmp.append(data[i])

		else:
			if l1 == 0:
				ls[-1].append(data[i])
			else:
				tmp.append(data[i])

		i += 1

	if len(ls) == 1:
		return ls[0]

	while [] in ls:
		ls.remove([])

	i = 0
	while i < len(ls):
		e = tree(ls[i])
		#if len(e) == 1:
		#	e = e[0]

		ls[i] = e
		i += 1

	return ls

def astree(data):
	pass

def asttest(filename="test/test.hl"):
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
	cst = tree(lex)
	print(cst, "\n")

if __name__ == "__main__":
	asttest()
