file_0 = open("1.txt","r")

coeff_and_1=[]
for line in file_0:
	line_1=line.rstrip().split()
	coeff_and_1.append(line_1[0]+" "+line_1[1]+" "+str((float(line_1[0])-float(line_1[1]))/float(line_1[0]))+" 1")
file_0.close()
file_0 = open("1.txt","w")
for line in coeff_and_1:
	print>>file_0, line

