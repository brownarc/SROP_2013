File = open ("Sample_Data.txt", "w")

user_input = raw_input ("Insert a number: ")

count = 0

File.write ("Name \tDemand\n")

while count < int (user_input):
    File.write ("Item" + str (count + 1) + "\t0.00521\n")
    count += 1
File.close()
