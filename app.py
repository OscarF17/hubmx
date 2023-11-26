from flask import Flask, Response, render_template, redirect, request
from flask_mysqldb import MySQL
from tensorflow.keras.models import load_model
from transformers import pipeline
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

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
    return render_template('index.html', reviews=reviews)

# Insertar contenidos de la reseña
@app.route('/insertReview', methods=['POST'])
def inserReview():
    user = request.form['user']
    text = request.form['text']
    analysis = feelings_analyzer(text)
    sentiment = analysis[0]['label']
    cursor = mysql.connection.cursor()
    cursor.callproc('createReview', [user, text, sentiment])
    cursor.connection.commit()
    cursor.close()
    return redirect('/')


@app.route('/model')
def model():
    return render_template('model.html')

@app.route('/predict', methods=['GET'])
def predict():
    company = request.args.get('company')
    show_future(company)
    return render_template('predict.html', company=company)



def show_future(company, future_days=15):
  # Load data
  csv = "datos/" + company + "_2020_2023.csv"
  data = pd.read_csv(csv, date_parser=True)
  data.set_index('Date', inplace=True)

  # Scale data
  scaler = MinMaxScaler(feature_range=(0, 1))
  scaled_data = scaler.fit_transform(data['Close'].values.reshape(-1, 1))

  # Create sequences
  sequence = 60
  x = []
  y = []

  for i in range(sequence, len(scaled_data)):
      x.append(scaled_data[i - sequence:i])
      y.append(scaled_data[i, 0])

  x, y = np.array(x), np.array(y)

  # Predictions for existing data
  predicted_prices_scaled = modelo.predict(x)
  predicted_prices = scaler.inverse_transform(predicted_prices_scaled)
  real_prices = scaler.inverse_transform(y.reshape(-1, 1))

  # Generate future dates
  future_dates_og = pd.date_range(start=data.index[-1], periods=future_days + 1, freq='B')[1:]
  future_dates = []
  i = 0
  for date in future_dates_og:
    future_dates.append(str(date))


  # Predict future prices
  future_x = []
  last_sequence = scaled_data[-sequence:]
  for _ in range(future_days):
      # Use your model to predict the next day
      future_prediction_scaled = modelo.predict(last_sequence.reshape(1, sequence, 1))
      future_price = scaler.inverse_transform(future_prediction_scaled)[0, 0]

      # Update the sequence for the next prediction
      last_sequence = np.append(last_sequence[1:], future_prediction_scaled)

      # Append the prediction to the future_x list
      future_x.append(future_price)

  # Plotting
  plt.figure(figsize=(14, 7))
  # Solamente mostrar cierto número de días reales
  plt.plot(data.index[-90:], real_prices[-90:], label='Precios reales', color='blue')
  plt.plot(future_dates, future_x, label='Predicciones', color='green', linestyle='dashed')
  plt.title(f"Precios reales contra predicciones ({company})")
  plt.xlabel('Fecha')
  plt.ylabel('Precio ($)')
  plt.legend()
  plt.savefig(f"static/img/{company}.png")



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
