import re

p = re.match(r"^/$", "/")
# print(p.groupdict())

print(re.sub(":([\w]+)", r"(?P<\1>[\\w]+)", "/route/:pollo"))
