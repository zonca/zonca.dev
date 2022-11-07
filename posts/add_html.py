# with is like your try .. finally block in this case
import sys

filename = sys.argv[1]

with open(filename, "r") as file:
    # read a list of lines into data
    data = file.readlines()

# now change the 2nd line, note that you have to add a newline
for line_num, line in enumerate(data[:10]):
    if line.startswith("aliases"):
        data[line_num + 1] = data[line_num + 1].replace("\n", ".html\n")
        # and write everything back
        with open(filename, "w") as file:
            file.writelines(data)
        sys.exit(0)

print("Cannot find aliases line in " + filename)
