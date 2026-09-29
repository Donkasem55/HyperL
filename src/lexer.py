from util import *

# primitives
import lex.prim as prim

def token(data):
	ret = [""]
	flag = [False, False, False]
	j = 0
	while j < len(data):
		i = data[j]
		if strifin(i, ";,!$%(){}[]"):
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
				pass
			else:
				ret[-1] += i

		j += 1
	
	while "" in ret:
		ret.remove("")

	return ret

def lextest(filename="test/test.hl"):
	with open(filename) as f:
		d = f.read()
	print(token(d))

if __name__ == "__main__":
	lextest()
