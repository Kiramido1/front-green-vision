from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split

# تحضير البيانات للنموذج
# نستخدم متوسط NDVI لكل صورة كمتغير تابع
data = mean_ndvi.reshape(-1, 1)

# تطبيع البيانات
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

# إنشاء مجموعات التدريب والاختبار
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

# استخدام 6 نقاط زمنية سابقة للتنبؤ بالنقطة التالية
sequence_length = 6
X, y = create_sequences(scaled_data, sequence_length)

# تقسيم البيانات
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# بناء نموذج LSTM
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(sequence_length, 1)))
model.add(Dropout(0.2))
model.add(LSTM(50))
model.add(Dropout(0.2))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mean_squared_error')

# تدريب النموذج
history = model.fit(
    X_train, y_train,
    epochs=50,
    batch_size=32,
    validation_data=(X_test, y_test),
    verbose=1
)

# تقييم النموذج
plt.figure(figsize=(10, 6))
plt.plot(history.history['loss'], label='خسارة التدريب')
plt.plot(history.history['val_loss'], label='خسارة التحقق')
plt.title('أداء النموذج')
plt.xlabel('Epoch')
plt.ylabel('الخسارة')
plt.legend()
plt.show()

# التنبؤ باستخدام النموذج
predictions = model.predict(X_test)
predictions = scaler.inverse_transform(predictions)
actual = scaler.inverse_transform(y_test)

# رسم النتائج
plt.figure(figsize=(12, 6))
plt.plot(actual, label='القيم الفعلية')
plt.plot(predictions, label='التنبؤات')
plt.title('مقارنة بين القيم الفعلية والتنبؤات')
plt.xlabel('الفترة الزمنية')
plt.ylabel('NDVI')
plt.legend()
plt.show()