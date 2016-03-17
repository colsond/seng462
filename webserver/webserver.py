from flask import Flask
app = Flask(__name__)

@app.route('/')
def transaction_request():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()