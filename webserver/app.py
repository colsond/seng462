from flask import Flask, render_template, request, jsonify
import random
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/trader')
def trader():
    print 'trader times?!'
    return render_template('trader.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():

    request_json = request.get_json()
    print request_json
    username = request_json.get("username", None)
    if username:
        print username
    else:
        print "No usename found"

    request_type = request_json.get("request_type", None)
    if request_type:
        print request_type
    else:
        print "No request_type found"

    tx_server = random.randint(1, 10)
    return jsonify({"tx_server": tx_server})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='44442')
