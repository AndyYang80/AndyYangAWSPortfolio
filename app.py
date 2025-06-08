import logging
import os
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, request, jsonify
from backend import response

if not os.path.exists('logs'):
    os.makedirs('logs')

file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
file_handler.setFormatter(formatter)

app = Flask(__name__)

# Attach handler to app.logger
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    message = request.form['msg']
    try:
        airesponse = response(message)
    except Exception as e:
        app.logger.info(e)
        exit(1)
    return airesponse

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)