import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np

data_dict = {}
commands = ["ADD",
"QUOTE",
"BUY",
"COMMIT_BUY",
"CANCEL_BUY",
"SELL",
"COMMIT_SELL",
"CANCEL_SELL",
"SET_BUY_AMOUNT",
"CANCEL_SET_BUY",
"SET_BUY_TRIGGER",
"SET_SELL_AMOUNT",
"SET_SELL_TRIGGER",
"CANCEL_SET_SELL",
"DUMPLOG",
"DISPLAY_SUMMARY",
"SELECT",
"FILTER",
"UPDATE",
"INSERT",
"DELETE"]

for command in commands:
    data_dict[command] = []

for i in range(1,10):
    outfile = "out%d.txt" % i
    with open(outfile) as f:
        content = f.readlines()
	for line in content:
	    if ":" in line:
		values = line.split(":")
		command = values[0].strip(" ")
		time = values[1].strip(" ")
		data_dict[command].append(time)

for command in commands:
    values = np.array(data_dict[command])
    data = [
        go.Histogram(
            x=values
        )
    ]
    plot_url = py.plot(data, filename='%s-histogram-2' % command)


