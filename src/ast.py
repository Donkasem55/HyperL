from util import *
from lexer import *
from const import *
from evalexpr import *


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
					tmparr[-1].append(tmp2)
				tmp2 = []
				if tmp:
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
					tmparr[-1].append(tmp2)
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
	cst = cstree(lex)
	import pprint
	pprint.pp(cst, width=40, indent=4)

if __name__ == "__main__":
	asttest()
