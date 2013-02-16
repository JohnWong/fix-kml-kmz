import re
read_file = open("./Mars2Wgs.txt")
write_file = open("./Mars2Wgs_converted.txt", mode="w")
pattern = re.compile("[\d]+")
while 1:
    line = read_file.readline()
    if not line:
        break
    line = line.rstrip()
    numbers = pattern.findall(line)
    write_file.write("%s %s,%s %s," % (numbers[0], numbers[1], numbers[2], numbers[3]))
    
write_file.close()
print("End")
