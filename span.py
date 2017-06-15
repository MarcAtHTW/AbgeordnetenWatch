import re
string = 'This sfsdfsfs is the next step'
m = re.search("is", string)

iter = re.finditer(r"\bis\b", string)
indices = [(m.start(0), m.end(0)) for m in iter]
print(indices)