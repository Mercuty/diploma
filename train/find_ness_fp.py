
file = open('all1.csv','r')
fp=0.026
tp=0.82

r_fp=1
ones=[]
zeros=[]
for line in file:
	line = line.rstrip().split(',')
	if int(line[3]) == 1:
		ones.append(float(line[2]))
	else:
		zeros.append(float(line[2]))
tr=1
print(zeros)
while (r_fp>1-fp):
	col=0
	for num in zeros:
		if num>=tr:
			col+=1
	print(col, len(zeros))
	r_fp=(len(zeros)-float(col))/len(zeros)
	print(r_fp)
	print(tr)
	tr-=0.01
print (r_fp, tr)