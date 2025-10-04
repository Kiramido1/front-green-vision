# نظام التنبؤ بمستويات الجفاف

![صورة توضيحية للجفاف](https://via.placeholder.com/800x400?text=نظام+التنبؤ+بمستويات+الجفاف)

## نظرة عامة

هذا المشروع عبارة عن نظام تنبؤ متقدم يستخدم تقنيات التعلم الآلي للتنبؤ بمستويات الجفاف المختلفة (D0 إلى D4) في المناطق الجغرافية. يعتمد النظام على بيانات تاريخية للجفاف ويستخدم نماذج XGBoost المحسنة لتقديم تنبؤات دقيقة.

## مستويات الجفاف

النظام يتنبأ بالنسب المئوية للمناطق التي تعاني من مستويات الجفاف التالية:

| المستوى | الوصف | اللون على الخريطة |
|---------|-------|-------------------|
| **D0** | جفاف غير طبيعي | أصفر فاتح |
| **D1** | جفاف معتدل | أصفر |
| **D2** | جفاف شديد | برتقالي |
| **D3** | جفاف شديد جداً | برتقالي محمر |
| **D4** | جفاف استثنائي | أحمر |

## محتويات المشروع

- `main.py`: الكود الرئيسي لمعالجة البيانات وتدريب النماذج
- `models/`: مجلد يحتوي على النماذج المدربة والمعلومات المرتبطة بها
  - `D0_best_model.pkl`: نموذج التنبؤ لمستوى D0
  - `D0_model_info.pkl`: معلومات النموذج (المتغيرات، المقاييس، إلخ)
  - (وهكذا لباقي المستويات D1-D4)
- `dm_export_20100101_20251001.csv`: بيانات الجفاف التاريخية
- صور مختلفة (`.png`) تمثل تحليلات البيانات

## شرح مفصل لملفات النماذج

### أنواع ملفات النماذج

مجلد `models` يحتوي على نوعين من الملفات لكل مستوى من مستويات الجفاف (D0 إلى D4):

1. **ملفات النموذج (`*_best_model.pkl`):**
   - تحتوي على النموذج المدرب نفسه (XGBoost)
   - هذه هي الملفات التي تقوم بعملية التنبؤ الفعلية
   - تحتوي على الهيكل الداخلي للنموذج، والأوزان، وشجرة القرارات
   - حجمها أكبر نسبياً لأنها تحتوي على بنية النموذج كاملة

2. **ملفات المعلومات (`*_model_info.pkl`):**
   - تحتوي على معلومات ضرورية لاستخدام النموذج بشكل صحيح
   - تتضمن:
     - `feature_columns`: قائمة بأسماء المتغيرات التي يحتاجها النموذج بالترتيب الصحيح
     - `scaler`: كائن StandardScaler المستخدم لتطبيع البيانات قبل التنبؤ
     - `performance_metrics`: مقاييس أداء النموذج (RMSE, MAE, R²)
     - `model_parameters`: المعلمات المثلى للنموذج
     - معلومات أخرى مفيدة للتنبؤ والتقييم

### لماذا نحتاج كلا النوعين من الملفات؟

**يجب استخدام كلا النوعين من الملفات معاً** للأسباب التالية:

1. **ملف النموذج وحده غير كافٍ** لأنه:
   - لا يحتوي على معلومات عن المتغيرات المطلوبة وترتيبها
   - لا يحتوي على أداة التطبيع (scaler) المستخدمة أثناء التدريب
   - لا يمكنه معالجة البيانات الخام مباشرة

2. **ملف المعلومات وحده غير كافٍ** لأنه:
   - لا يحتوي على النموذج نفسه
   - لا يمكنه إجراء التنبؤات

3. **استخدامهما معاً يوفر**:
   - معرفة المتغيرات المطلوبة بالضبط
   - تطبيع البيانات بنفس الطريقة المستخدمة أثناء التدريب
   - إجراء التنبؤات بدقة عالية
   - تقييم جودة التنبؤات

### محتويات ملف المعلومات بالتفصيل

عند فتح ملف المعلومات (مثل `D0_model_info.pkl`)، ستجد قاموساً (dictionary) يحتوي على المفاتيح التالية:

```python
{
    'feature_columns': [...],  # قائمة بأسماء المتغيرات المستخدمة في النموذج
    'scaler': StandardScaler(),  # كائن لتطبيع البيانات
    'performance_metrics': {
        'rmse': 1.23,  # جذر متوسط مربع الخطأ
        'mae': 0.98,   # متوسط الخطأ المطلق
        'r2': 0.95     # معامل التحديد
    },
    'model_parameters': {
        'max_depth': 6,
        'learning_rate': 0.1,
        'n_estimators': 100,
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        # ... وغيرها من المعلمات
    }
}
```

### مثال تفصيلي لاستخدام ملفات النموذج والمعلومات معاً

فيما يلي مثال كامل لكيفية تحميل واستخدام ملفات النموذج والمعلومات معاً للتنبؤ بمستويات الجفاف:

```python
import pickle
import pandas as pd
import numpy as np
from datetime import datetime

# 1. تحميل ملف النموذج وملف المعلومات
def load_model_and_info(drought_level):
    """
    تحميل النموذج والمعلومات المرتبطة به لمستوى جفاف معين
    
    المعلمات:
        drought_level (str): مستوى الجفاف ('D0', 'D1', 'D2', 'D3', 'D4')
        
    العائد:
        tuple: (النموذج، معلومات النموذج)
    """
    # تحميل النموذج
    model_path = f"models/{drought_level}_best_model.pkl"
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # تحميل معلومات النموذج
    info_path = f"models/{drought_level}_model_info.pkl"
    with open(info_path, 'rb') as f:
        model_info = pickle.load(f)
    
    return model, model_info

# 2. تحضير البيانات للتنبؤ
def prepare_data_for_prediction(historical_data, model_info):
    """
    تحضير البيانات للتنبؤ باستخدام معلومات النموذج
    
    المعلمات:
        historical_data (DataFrame): بيانات تاريخية تحتوي على الأسابيع السابقة
        model_info (dict): معلومات النموذج المحملة من ملف المعلومات
        
    العائد:
        DataFrame: البيانات المعدة للتنبؤ
    """
    # استخراج المتغيرات المطلوبة وأداة التطبيع من معلومات النموذج
    feature_columns = model_info['feature_columns']
    scaler = model_info['scaler']
    
    # التأكد من أن البيانات تحتوي على جميع المتغيرات المطلوبة
    # (هنا نفترض أن البيانات تم معالجتها مسبقاً وتحتوي على جميع المتغيرات)
    
    # اختيار المتغيرات المطلوبة فقط بنفس الترتيب المستخدم في التدريب
    X = historical_data[feature_columns].copy()
    
    # تطبيع البيانات باستخدام نفس أداة التطبيع المستخدمة في التدريب
    X_scaled = scaler.transform(X)
    
    return X_scaled

# 3. التنبؤ باستخدام النموذج
def predict_drought_level(model, X_scaled):
    """
    التنبؤ بمستوى الجفاف باستخدام النموذج المحمل
    
    المعلمات:
        model: النموذج المحمل
        X_scaled (array): البيانات المطبعة للتنبؤ
        
    العائد:
        float: القيمة المتنبأ بها لمستوى الجفاف
    """
    # التنبؤ باستخدام النموذج
    prediction = model.predict(X_scaled)
    
    return prediction[0]  # إرجاع القيمة الأولى فقط (للمثال)

# 4. مثال كامل للاستخدام
def example_usage():
    """
    مثال كامل لاستخدام النماذج للتنبؤ بمستويات الجفاف
    """
    # افتراض أن لدينا بيانات تاريخية جاهزة (يجب تحضيرها في الواقع)
    # هذا مجرد مثال، في التطبيق الحقيقي ستحتاج لمعالجة البيانات الخام أولاً
    historical_data = pd.DataFrame({
        'Year': [2023],
        'Month': [6],
        'Week': [25],
        'DayOfYear': [180],
        'Season': ['Summer'],
        'D0': [10.5],
        'D1': [5.2],
        'D2': [2.1],
        'D3': [1.0],
        'D4': [0.5],
        'D0_lag_1': [10.2],
        'D0_lag_2': [9.8],
        # ... وهكذا لجميع المتغيرات المطلوبة
    })
    
    # تحميل النموذج ومعلوماته لمستوى D0
    drought_level = 'D0'
    model, model_info = load_model_and_info(drought_level)
    
    # تحضير البيانات للتنبؤ
    X_scaled = prepare_data_for_prediction(historical_data, model_info)
    
    # التنبؤ بمستوى الجفاف
    prediction = predict_drought_level(model, X_scaled)
    
    print(f"التنبؤ بمستوى الجفاف {drought_level}: {prediction:.2f}")
    
    # يمكن تكرار نفس العملية لباقي مستويات الجفاف (D1-D4)
```

### الأخطاء الشائعة عند استخدام ملفات النموذج

فيما يلي بعض الأخطاء الشائعة التي قد تواجهها عند استخدام ملفات النموذج والمعلومات، وكيفية تجنبها:

1. **عدم تحميل ملف المعلومات:**
   - **الخطأ:** استخدام النموذج مباشرة دون تحميل ملف المعلومات
   - **الحل:** تأكد دائماً من تحميل كلا الملفين معاً

2. **ترتيب المتغيرات غير صحيح:**
   - **الخطأ:** تقديم المتغيرات للنموذج بترتيب مختلف عن الترتيب المستخدم في التدريب
   - **الحل:** استخدم `feature_columns` من ملف المعلومات لضمان نفس الترتيب

3. **عدم تطبيع البيانات:**
   - **الخطأ:** تقديم بيانات خام للنموذج دون تطبيعها
   - **الحل:** استخدم `scaler` من ملف المعلومات لتطبيع البيانات قبل التنبؤ

4. **نقص في المتغيرات المطلوبة:**
   - **الخطأ:** عدم توفير جميع المتغيرات التي يتوقعها النموذج
   - **الحل:** تأكد من أن بياناتك تحتوي على جميع المتغيرات المذكورة في `feature_columns`

5. **استخدام إصدارات مختلفة من المكتبات:**
   - **الخطأ:** استخدام إصدار مختلف من مكتبة XGBoost عن الإصدار المستخدم في التدريب
   - **الحل:** تأكد من تثبيت نفس إصدارات المكتبات المستخدمة في التدريب

## متطلبات النظام

لتشغيل هذا المشروع، تحتاج إلى:

- Python 3.7 أو أحدث
- المكتبات التالية:
  ```
  pandas
  numpy
  matplotlib
  seaborn
  scikit-learn
  xgboost
  pickle
  ```

يمكنك تثبيت المكتبات المطلوبة باستخدام الأمر:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost
```

## كيفية استخدام النماذج

### 1. تحميل النماذج

```python
import pickle
import pandas as pd

# دالة لتحميل النموذج ومعلوماته
def load_model_and_info(drought_level):
    model_path = f'models/{drought_level}_best_model.pkl'
    info_path = f'models/{drought_level}_model_info.pkl'
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    with open(info_path, 'rb') as f:
        model_info = pickle.load(f)
    
    return model, model_info

# تحميل نموذج معين (مثلاً D0)
model_d0, model_info_d0 = load_model_and_info('D0')
```

### 2. فهم المتغيرات المطلوبة

لاستخدام النماذج، تحتاج إلى البيانات التالية:

1. **بيانات الجفاف التاريخية** (لآخر 8 أسابيع على الأقل):
   - `None`: النسبة المئوية للمناطق التي لا تعاني من الجفاف
   - `D0` إلى `D4`: النسب المئوية للمناطق التي تعاني من مستويات الجفاف المختلفة

2. **التاريخ**: لاستخراج المتغيرات الزمنية مثل السنة، الشهر، الأسبوع، يوم السنة، والموسم

### 3. إعداد البيانات للتنبؤ

```python
def prepare_data_for_prediction(input_data):
    """
    إعداد البيانات للتنبؤ
    
    input_data: DataFrame يحتوي على البيانات التاريخية للجفاف والتاريخ
    """
    # تحويل التاريخ
    input_data["MapDate"] = pd.to_datetime(input_data["MapDate"])
    
    # إضافة متغيرات زمنية
    input_data['Year'] = input_data['MapDate'].dt.year
    input_data['Month'] = input_data['MapDate'].dt.month
    input_data['Week'] = input_data['MapDate'].dt.isocalendar().week
    input_data['DayOfYear'] = input_data['MapDate'].dt.dayofyear
    
    # تحويل الشهور إلى فصول
    season_map = {1: 'Winter', 2: 'Winter', 3: 'Winter', 
                  4: 'Spring', 5: 'Spring', 6: 'Spring',
                  7: 'Summer', 8: 'Summer', 9: 'Summer',
                  10: 'Fall', 11: 'Fall', 12: 'Fall'}
    input_data['Season'] = input_data['Month'].map(season_map)
    
    # إنشاء مؤشر شدة الجفاف
    input_data['Drought_Severity_Index'] = (0*input_data['None'] + 1*input_data['D0'] + 2*input_data['D1'] + 
                                           3*input_data['D2'] + 4*input_data['D3'] + 5*input_data['D4']) / 100
    
    # إنشاء متغيرات متأخرة (lag features)
    for lag in [1, 2, 4, 8]:
        for col in ['D0', 'D1', 'D2', 'D3', 'D4', 'None']:
            input_data[f'{col}_lag_{lag}'] = input_data[col].shift(lag)
    
    # إنشاء متغيرات متحركة (rolling features)
    for window in [4, 8]:
        for col in ['D0', 'D1', 'D2', 'D3', 'D4', 'None']:
            input_data[f'{col}_rolling_mean_{window}'] = input_data[col].rolling(window=window).mean()
            input_data[f'{col}_rolling_std_{window}'] = input_data[col].rolling(window=window).std()
    
    # تحويل المتغيرات الفئوية إلى متغيرات وهمية
    input_data = pd.get_dummies(input_data, columns=['Season'], drop_first=True)
    
    return input_data
```

### 4. استخدام النماذج للتنبؤ

```python
def predict_drought_level(input_data, drought_level):
    """
    التنبؤ بمستوى جفاف معين
    
    input_data: DataFrame يحتوي على البيانات المعدة
    drought_level: مستوى الجفاف المراد التنبؤ به (D0, D1, D2, D3, D4)
    """
    # تحميل النموذج ومعلوماته
    model, model_info = load_model_and_info(drought_level)
    
    # استخراج المتغيرات المطلوبة للنموذج
    features = model_info['feature_columns']
    scaler = model_info['scaler']
    
    # التأكد من وجود جميع المتغيرات المطلوبة
    for feature in features:
        if feature not in input_data.columns:
            input_data[feature] = 0
    
    # تطبيع البيانات
    X_pred = input_data[features].values
    X_pred_scaled = scaler.transform(X_pred)
    
    # التنبؤ
    prediction = model.predict(X_pred_scaled)
    
    return prediction
```

### 5. مثال كامل للاستخدام

```python
import pandas as pd
import pickle
import numpy as np

# بيانات تاريخية للجفاف (مثال)
historical_data = pd.DataFrame({
    'MapDate': pd.date_range(start='2023-01-01', periods=10, freq='W'),
    'None': [20, 25, 30, 35, 40, 45, 50, 55, 60, 65],
    'D0': [30, 28, 26, 24, 22, 20, 18, 16, 14, 12],
    'D1': [20, 19, 18, 17, 16, 15, 14, 13, 12, 11],
    'D2': [15, 14, 13, 12, 11, 10, 9, 8, 7, 6],
    'D3': [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
    'D4': [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
})

# إعداد البيانات
prepared_data = prepare_data_for_prediction(historical_data)

# الحصول على الصف الأخير للتنبؤ
prediction_row = prepared_data.iloc[-1:].copy()

# التنبؤ لكل مستوى من مستويات الجفاف
predictions = {}
for level in ['D0', 'D1', 'D2', 'D3', 'D4']:
    prediction = predict_drought_level(prediction_row, level)[0]
    predictions[level] = prediction

# عرض النتائج
print("التنبؤات لتاريخ", prediction_row['MapDate'].iloc[0])
for level, value in predictions.items():
    print(f"{level}: {value:.2f}%")
```

## دمج النماذج في تطبيق ويب

### 1. إنشاء واجهة برمجة تطبيقات (API)

يمكن دمج النماذج في تطبيق ويب باستخدام إطار عمل مثل Flask أو Django:

```python
from flask import Flask, request, jsonify
import pandas as pd
import pickle

app = Flask(__name__)

# تحميل النماذج عند بدء التطبيق
models = {}
model_infos = {}
for level in ['D0', 'D1', 'D2', 'D3', 'D4']:
    model_path = f'models/{level}_best_model.pkl'
    info_path = f'models/{level}_model_info.pkl'
    
    with open(model_path, 'rb') as f:
        models[level] = pickle.load(f)
    
    with open(info_path, 'rb') as f:
        model_infos[level] = pickle.load(f)

@app.route('/api/predict', methods=['POST'])
def predict():
    # استلام البيانات
    data = request.json
    historical_data = pd.DataFrame(data['historical_data'])
    
    # إعداد البيانات
    prepared_data = prepare_data_for_prediction(historical_data)
    prediction_row = prepared_data.iloc[-1:].copy()
    
    # التنبؤ
    predictions = {}
    for level in ['D0', 'D1', 'D2', 'D3', 'D4']:
        model = models[level]
        model_info = model_infos[level]
        features = model_info['feature_columns']
        scaler = model_info['scaler']
        
        for feature in features:
            if feature not in prediction_row.columns:
                prediction_row[feature] = 0
        
        X_pred = prediction_row[features].values
        X_pred_scaled = scaler.transform(X_pred)
        prediction = float(model.predict(X_pred_scaled)[0])
        predictions[level] = prediction
    
    return jsonify(predictions)

if __name__ == '__main__':
    app.run(debug=True)
```

### 2. عرض النتائج على خريطة تفاعلية

لعرض النتائج على خريطة تفاعلية، يمكن استخدام مكتبة Leaflet.js في الواجهة الأمامية:

```html
<!DOCTYPE html>
<html>
<head>
    <title>خريطة مستويات الجفاف</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <style>
        #map {
            height: 600px;
            width: 100%;
        }
        .legend {
            background: white;
            padding: 10px;
            border-radius: 5px;
        }
        .legend-item {
            margin-bottom: 5px;
        }
        .color-box {
            display: inline-block;
            width: 20px;
            height: 20px;
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <h1>خريطة التنبؤ بمستويات الجفاف</h1>
    <div id="map"></div>
    
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        // إنشاء الخريطة
        const map = L.map('map').setView([30, 0], 2);
        
        // إضافة طبقة الخريطة الأساسية
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);
        
        // ألوان مستويات الجفاف
        const droughtColors = {
            'D0': '#ffeb3b', // أصفر فاتح
            'D1': '#ffc107', // أصفر
            'D2': '#ff9800', // برتقالي
            'D3': '#ff5722', // برتقالي محمر
            'D4': '#f44336'  // أحمر
        };
        
        // دالة لتحديد لون المنطقة بناءً على مستويات الجفاف
        function getRegionColor(droughtLevels) {
            // تحديد المستوى الأعلى
            if (droughtLevels.D4 > 20) return droughtColors.D4;
            if (droughtLevels.D3 > 20) return droughtColors.D3;
            if (droughtLevels.D2 > 20) return droughtColors.D2;
            if (droughtLevels.D1 > 20) return droughtColors.D1;
            if (droughtLevels.D0 > 20) return droughtColors.D0;
            return '#4CAF50'; // أخضر (لا يوجد جفاف)
        }
        
        // إضافة وسيلة إيضاح
        const legend = L.control({ position: 'bottomright' });
        legend.onAdd = function(map) {
            const div = L.DomUtil.create('div', 'legend');
            div.innerHTML += '<h4>مستويات الجفاف</h4>';
            div.innerHTML += '<div class="legend-item"><span class="color-box" style="background: #4CAF50"></span>لا يوجد جفاف</div>';
            div.innerHTML += '<div class="legend-item"><span class="color-box" style="background: ' + droughtColors.D0 + '"></span>D0 - جفاف غير طبيعي</div>';
            div.innerHTML += '<div class="legend-item"><span class="color-box" style="background: ' + droughtColors.D1 + '"></span>D1 - جفاف معتدل</div>';
            div.innerHTML += '<div class="legend-item"><span class="color-box" style="background: ' + droughtColors.D2 + '"></span>D2 - جفاف شديد</div>';
            div.innerHTML += '<div class="legend-item"><span class="color-box" style="background: ' + droughtColors.D3 + '"></span>D3 - جفاف شديد جداً</div>';
            div.innerHTML += '<div class="legend-item"><span class="color-box" style="background: ' + droughtColors.D4 + '"></span>D4 - جفاف استثنائي</div>';
            return div;
        };
        legend.addTo(map);
        
        // استدعاء API للحصول على التنبؤات وعرضها على الخريطة
        async function fetchPredictionsAndUpdateMap() {
            // بيانات المثال (في التطبيق الحقيقي، ستأتي من قاعدة البيانات)
            const historicalData = {
                'MapDate': ['2023-01-01', '2023-01-08', '2023-01-15', '2023-01-22', 
                           '2023-01-29', '2023-02-05', '2023-02-12', '2023-02-19', 
                           '2023-02-26', '2023-03-05'],
                'None': [20, 25, 30, 35, 40, 45, 50, 55, 60, 65],
                'D0': [30, 28, 26, 24, 22, 20, 18, 16, 14, 12],
                'D1': [20, 19, 18, 17, 16, 15, 14, 13, 12, 11],
                'D2': [15, 14, 13, 12, 11, 10, 9, 8, 7, 6],
                'D3': [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
                'D4': [5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
            };
            
            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        historical_data: historicalData
                    }),
                });
                
                const predictions = await response.json();
                console.log('التنبؤات:', predictions);
                
                // في التطبيق الحقيقي، ستقوم بتحديث الخريطة بناءً على التنبؤات
                // هذا مجرد مثال لإظهار كيفية استخدام التنبؤات
                
                // مثال: إضافة مناطق عشوائية للتوضيح
                const regions = [
                    { name: 'منطقة 1', coords: [[25, -10], [25, 10], [35, 10], [35, -10]] },
                    { name: 'منطقة 2', coords: [[15, -20], [15, 0], [25, 0], [25, -20]] },
                    { name: 'منطقة 3', coords: [[15, 0], [15, 20], [25, 20], [25, 0]] }
                ];
                
                regions.forEach((region, index) => {
                    // تعيين قيم مختلفة لكل منطقة للتوضيح
                    const regionPredictions = { ...predictions };
                    if (index === 0) regionPredictions.D2 = 30; // زيادة D2 للمنطقة 1
                    if (index === 1) regionPredictions.D4 = 25; // زيادة D4 للمنطقة 2
                    
                    const color = getRegionColor(regionPredictions);
                    
                    L.polygon(region.coords, {
                        color: 'black',
                        weight: 1,
                        fillColor: color,
                        fillOpacity: 0.7
                    }).addTo(map).bindPopup(`
                        <h3>${region.name}</h3>
                        <p>D0: ${regionPredictions.D0.toFixed(2)}%</p>
                        <p>D1: ${regionPredictions.D1.toFixed(2)}%</p>
                        <p>D2: ${regionPredictions.D2.toFixed(2)}%</p>
                        <p>D3: ${regionPredictions.D3.toFixed(2)}%</p>
                        <p>D4: ${regionPredictions.D4.toFixed(2)}%</p>
                    `);
                });
                
            } catch (error) {
                console.error('خطأ في الحصول على التنبؤات:', error);
            }
        }
        
        // استدعاء الدالة لتحديث الخريطة
        fetchPredictionsAndUpdateMap();
    </script>
</body>
</html>
```

## شرح المتغيرات المستخدمة في النماذج

### المتغيرات الأساسية

1. **متغيرات الجفاف الأساسية**:
   - `None`: النسبة المئوية للمناطق التي لا تعاني من الجفاف
   - `D0` إلى `D4`: النسب المئوية للمناطق التي تعاني من مستويات الجفاف المختلفة

2. **المتغيرات الزمنية**:
   - `Year`: السنة
   - `Month`: الشهر (1-12)
   - `Week`: الأسبوع من السنة (1-53)
   - `DayOfYear`: اليوم من السنة (1-366)
   - `Season`: الموسم (Winter, Spring, Summer, Fall)

### المتغيرات المشتقة

1. **مؤشر شدة الجفاف**:
   - `Drought_Severity_Index`: مؤشر مركب يحسب من خلال ترجيح مستويات الجفاف المختلفة

2. **المتغيرات المتأخرة (Lag Features)**:
   - `D0_lag_1`, `D0_lag_2`, `D0_lag_4`, `D0_lag_8`: قيم D0 قبل 1، 2، 4، 8 أسابيع
   - (وهكذا لباقي المستويات D1-D4 و None)

3. **المتغيرات المتحركة (Rolling Features)**:
   - `D0_rolling_mean_4`: المتوسط المتحرك لـ D0 خلال 4 أسابيع
   - `D0_rolling_std_4`: الانحراف المعياري المتحرك لـ D0 خلال 4 أسابيع
   - (وهكذا لنوافذ 8 أسابيع ولباقي المستويات D1-D4 و None)

## الأسئلة الشائعة

### 1. ما هي دقة النماذج؟

النماذج تحقق دقة عالية مع معامل تحديد (R²) يتراوح بين 0.93 و0.99، وخطأ جذر متوسط مربعات (RMSE) منخفض، مما يشير إلى أداء ممتاز في التنبؤ بمستويات الجفاف.

### 2. كم من البيانات التاريخية أحتاج لإجراء تنبؤ؟

تحتاج على الأقل إلى 8 أسابيع من البيانات التاريخية لإنشاء المتغيرات المتأخرة والمتحركة اللازمة للنماذج.

### 3. هل يمكنني التنبؤ بمستويات الجفاف لأكثر من أسبوع في المستقبل؟

نعم، يمكنك استخدام التنبؤات كمدخلات للنموذج للتنبؤ بالأسابيع التالية، لكن دقة التنبؤات قد تنخفض كلما ابتعدت في المستقبل.

### 4. كيف يمكنني تحسين النماذج؟

يمكن تحسين النماذج من خلال:
- إضافة متغيرات مناخية إضافية (مثل هطول الأمطار، درجات الحرارة)
- تحديث النماذج بانتظام مع توفر بيانات جديدة
- تجربة تقنيات نمذجة أخرى أو مجموعات من النماذج

## المساهمة في المشروع

نرحب بمساهماتكم لتحسين هذا المشروع! يمكنكم:
1. إنشاء fork للمشروع
2. إنشاء فرع جديد للميزة التي تريدون إضافتها
3. إرسال طلب سحب (Pull Request) مع شرح التغييرات

## الترخيص

هذا المشروع مرخص تحت [رخصة MIT](https://opensource.org/licenses/MIT).

## الاتصال

إذا كان لديك أي أسئلة أو استفسارات، يرجى التواصل معنا عبر [البريد الإلكتروني](mailto:example@example.com).