from flask import Flask, Response, render_template
from flask_mysqldb import MySQL
from tensorflow.keras.models import load_model
from transformers import pipeline
from datetime import datetime, timedelta

app = Flask(__name__)

mysql = MySQL(app)

app.config['MYSQL_USER'] = 'usr'
app.config['MYSQL_PASSWORD'] = '123'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_DB'] = 'HubMX'

# Modelo para análisis sentimental
feelings_analyzer = pipeline(task = "text-classification", model="pysentimiento/robertuito-sentiment-analysis")

# Modelo para predecir stocks
modelo = load_model('modelo.h5')
print('hello world')

@app.route('/')
def index():
    cursor = mysql.connection.cursor()
    cursor.callproc('getReviews')
    reviews = cursor.fetchall()
    cursor.close()
    sentiment = feelings_analyzer('ESTOY MUY FELIZ')
    print(sentiment)
    return render_template('index.html', reviews=reviews)

@app.route('/insertReview', methods=['POST'])
def inserReview():
    user = request.form['user']
    text = request.form['text']
    sentiment = feelings_analyzer(text)
    return 'hola'


@app.route('/model')
def model():
    return render_template('model.html')

@app.route('/model/<string:company>')
def show_company(company):
    return render_template('company.html', company=company)




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
