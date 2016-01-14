import requests
import io

f = open("1userWorkLoad", 'r')
commands = []
for line in f:
	tokens = line.split()
	cmdNum = tokens[0]
	request = tokens[1].split(',')
	if request[0] not in commands:
		commands.append(request[0])

print commands


