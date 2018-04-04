
train=[]
f = open("1_all.txt",'r')
for line in f:
	line=line.rstrip().split(" ")
	line.append("1")
	train.append(line)
f.close()
f = open("0_all.txt",'r')
for line in f:
	line=line.rstrip().split(" ")
	line.append("0")
	train.append(line)
print(train)

