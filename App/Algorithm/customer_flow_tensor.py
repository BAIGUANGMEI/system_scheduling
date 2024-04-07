import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam

day = 1
month = 12
year = 2023

history_flow = []
date_list = list(pd.bdate_range('9/1/2023',f'{month}/{day}/{year}').strftime("%Y-%m-%d"))
date = []
time = ['8:00','13:00','18:00']

for i in range(len(date_list)):
    for j in range(3):
        date.append(date_list[i]+' '+time[j])
    history_flow.append(random.randint(50, 200))
    history_flow.append(random.randint(100,400))
    history_flow.append(random.randint(100,400))

df = pd.DataFrame()

df['date'] = date
df['date'] = pd.to_datetime(df['date'])
df['flow'] = history_flow
print(df)

series = df.set_index(['date'], drop=True)
plt.figure(figsize=(10,6))

series['flow'].plot()
plt.show()
# print(series)

df.set_index('date', inplace=True)

# 数据预处理
scaler = MinMaxScaler(feature_range=(0, 1))
df_scaled = scaler.fit_transform(df)

# 创建时间序列数据集
def create_dataset(dataset, time_step=1):
    X, Y = [], []
    for i in range(len(dataset) - time_step - 1):
        a = dataset[i:(i + time_step), 0]
        X.append(a)
        Y.append(dataset[i + time_step, 0])
    return np.array(X), np.array(Y)

time_step = 14
X, Y = create_dataset(df_scaled, time_step)
X = X.reshape(X.shape[0], X.shape[1], 1)

# 分割数据集
train_size = int(len(X) * 0.70)
test_size = len(X) - train_size
X_train, X_test = X[0:train_size], X[train_size:len(X)]
Y_train, Y_test = Y[0:train_size], Y[train_size:len(Y)]

# 构建LSTM模型
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(time_step, 1)),
    LSTM(50),
    Dense(25),
    Dense(1)
])

model.compile(optimizer=Adam(learning_rate=0.01), loss='mean_squared_error')

# 训练模型
model.fit(X_train, Y_train, validation_data=(X_test, Y_test), epochs=500, batch_size=21)

# 预测函数
def predict_next_seven_days(model, last_days_data, scaler, days_to_predict=21):
    predictions = []
    current_batch = last_days_data.reshape((1, time_step, 1))

    for i in range(days_to_predict * 3):  # 一天三个时间段
        current_pred = model.predict(current_batch)[0]
        predictions.append(current_pred)
        current_batch = np.append(current_batch[:,1:,:], [[current_pred]], axis=1)

    original_scale_predictions = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
    return original_scale_predictions

# 使用模型预测未来七天
last_days_data = df_scaled[-time_step:]  # 取最后time_step天的数据进行预测
future_predictions = predict_next_seven_days(model, last_days_data, scaler)

print(future_predictions)

# 将预测数据转换为DataFrame
future_dates = pd.date_range(start=df.index[-1] + pd.Timedelta(hours=8), periods=len(future_predictions), freq='8H')
predicted_df = pd.DataFrame(future_predictions, index=future_dates, columns=['Predicted Flow'])

# 绘制图表
plt.figure(figsize=(12, 6))
plt.plot(df['flow'], label='Historical Flow')
plt.plot(predicted_df['Predicted Flow'], label='Predicted Flow', color='red')
plt.title('Flow Prediction for Next 7 Days')
plt.xlabel('Date')
plt.ylabel('Flow')
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

