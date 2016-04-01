from flask import Flask, render_template, request, jsonify
import random
import socket
app = Flask(__name__)

def make_request(transactionNum, command, user=None, stock_id=None, amount=None, filename=None):
    data = {
        'transactionNum': transactionNum,
        'command': command,
    }

    if user:
        data['user'] = user

    if stock_id:
        data['stock_id'] = stock_id

    if amount:
        data['amount'] = amount
    
    if filename:
        data['filename'] = filename

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = ('b133.seng.uvic.ca', 44422)

    sock.connect(server_address)

    try:
        # Send data
        message = str(data)
        sock.sendall(message)
        response = sock.recv(1024)
        print response

    finally:
        print >>sys.stderr, 'closing socket'
        sock.close()

    return response

@app.route('/',  methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        print request.form
        response = make_request(
            transactionNum=0, 
            command=request.form.get('request_type', None), 
            user=request.form.get('username', None),
            stock_id=request.form.get('stock_id', None), 
            amount=request.form.get('amount', None), 
            filename=request.form.get('filename', None)
        )
        # send request directly to transaction server if authenticated?
        return render_template('index.html')

if __name__ == "__main__":
    app.run()
