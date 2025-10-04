import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, TimeSeriesSplit, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
import xgboost as xgb
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=== تحليل بيانات الجفاف وبناء نموذج تنبؤي ===")

# 1. قراءة البيانات وفحصها
print("\n=== 1. قراءة البيانات وفحصها ===")
data = pd.read_csv('dm_export_20100101_20251001.csv')
print("شكل البيانات:", data.shape)
print("\nأول 5 صفوف:")
print(data.head())
print("\nمعلومات البيانات:")
print(data.info())
print("\nإحصائيات وصفية:")
print(data.describe())
print("\nالتحقق من القيم المفقودة:")
print(data.isnull().sum())

# 2. معالجة البيانات وتحويل التواريخ
print("\n=== 2. معالجة البيانات وتحويل التواريخ ===")
data["MapDate"] = pd.to_datetime(data["MapDate"].astype(str), format="%Y%m%d")
data["ValidStart"] = pd.to_datetime(data["ValidStart"])
data["ValidEnd"] = pd.to_datetime(data["ValidEnd"])

# إضافة متغيرات زمنية مفيدة
data['Year'] = data['MapDate'].dt.year
data['Month'] = data['MapDate'].dt.month
data['Week'] = data['MapDate'].dt.isocalendar().week
data['DayOfYear'] = data['MapDate'].dt.dayofyear

# تحويل الشهور إلى فصول (بدون استخدام pd.cut)
season_map = {1: 'Winter', 2: 'Winter', 3: 'Winter', 
              4: 'Spring', 5: 'Spring', 6: 'Spring',
              7: 'Summer', 8: 'Summer', 9: 'Summer',
              10: 'Fall', 11: 'Fall', 12: 'Fall'}
data['Season'] = data['Month'].map(season_map)

print("\nأنواع البيانات بعد المعالجة:")
print(data.dtypes)
print("\nالبيانات بعد إضافة المتغيرات الزمنية:")
print(data.head())

# 3. تحليل الاتجاهات والعلاقات
print("\n=== 3. تحليل الاتجاهات والعلاقات ===")

# تحليل اتجاه مستويات الجفاف عبر السنوات
plt.figure(figsize=(12, 6))
yearly_data = data.groupby('Year')[['None', 'D0', 'D1', 'D2', 'D3', 'D4']].mean()
yearly_data.plot(kind='line', marker='o')
plt.title('متوسط مستويات الجفاف عبر السنوات')
plt.xlabel('السنة')
plt.ylabel('النسبة المئوية')
plt.grid(True)
plt.savefig('drought_trends.png')
plt.close()

# تحليل موسمي
plt.figure(figsize=(14, 8))
seasonal_data = data.groupby(['Year', 'Season'])[['D0', 'D1', 'D2', 'D3', 'D4']].mean().reset_index()
for i, drought_level in enumerate(['D0', 'D1', 'D2', 'D3', 'D4']):
    plt.subplot(2, 3, i+1)
    for season in ['Winter', 'Spring', 'Summer', 'Fall']:
        season_data = seasonal_data[seasonal_data['Season'] == season]
        plt.plot(season_data['Year'], season_data[drought_level], marker='o', label=season)
    plt.title(f'اتجاه {drought_level} حسب الموسم')
    plt.xlabel('السنة')
    plt.ylabel('النسبة المئوية')
    plt.legend()
    plt.grid(True)
plt.tight_layout()
plt.savefig('seasonal_analysis.png')
plt.close()

# مصفوفة الارتباط
plt.figure(figsize=(10, 8))
correlation_matrix = data[['None', 'D0', 'D1', 'D2', 'D3', 'D4', 'Year', 'Month', 'Week']].corr()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('مصفوفة الارتباط بين المتغيرات')
plt.savefig('correlation_matrix.png')
plt.close()

print("تم حفظ الرسومات البيانية في ملفات PNG")

# 4. إعداد البيانات للنمذجة
print("\n=== 4. إعداد البيانات للنمذجة ===")

# إنشاء متغيرات إضافية
data['Drought_Severity_Index'] = (0*data['None'] + 1*data['D0'] + 2*data['D1'] + 
                                 3*data['D2'] + 4*data['D3'] + 5*data['D4']) / 100

# إنشاء متغيرات متأخرة (lag features)
for lag in [1, 2, 4, 8]:
    for col in ['D0', 'D1', 'D2', 'D3', 'D4', 'None']:
        data[f'{col}_lag_{lag}'] = data[col].shift(lag)

# إنشاء متغيرات متحركة (rolling features)
for window in [4, 8]:
    for col in ['D0', 'D1', 'D2', 'D3', 'D4', 'None']:
        data[f'{col}_rolling_mean_{window}'] = data[col].rolling(window=window).mean()
        data[f'{col}_rolling_std_{window}'] = data[col].rolling(window=window).std()

# حذف الصفوف التي تحتوي على قيم مفقودة بعد إنشاء المتغيرات المتأخرة والمتحركة
data = data.dropna()

print("شكل البيانات بعد إنشاء المتغيرات:", data.shape)

# 5. تقسيم البيانات إلى تدريب واختبار
print("\n=== 5. تقسيم البيانات إلى تدريب واختبار ===")

# تحديد المتغيرات المستقلة والتابعة
target_columns = ['D0', 'D1', 'D2', 'D3', 'D4']

# استبعاد الأعمدة غير المفيدة للنمذجة
exclude_columns = ['MapDate', 'AreaOfInterest', 'ValidStart', 'ValidEnd', 'StatisticFormatID', 'Season'] + target_columns

# تحديد المتغيرات المستقلة
feature_columns = [col for col in data.columns if col not in exclude_columns]

# تقسيم البيانات بناءً على التاريخ (80% تدريب، 20% اختبار)
split_date = data['MapDate'].quantile(0.8)
train_data = data[data['MapDate'] <= split_date]
test_data = data[data['MapDate'] > split_date]

print(f"تاريخ التقسيم: {split_date}")
print(f"حجم بيانات التدريب: {train_data.shape}")
print(f"حجم بيانات الاختبار: {test_data.shape}")

# 6. بناء وتدريب النماذج
print("\n=== 6. بناء وتدريب النماذج ===")

# تحضير البيانات - تحويل الأعمدة الفئوية إلى أعمدة رقمية
# تحويل عمود Season إلى متغيرات وهمية
data_encoded = pd.get_dummies(data, columns=['Season'], drop_first=True)

# تحديد المتغيرات المستقلة بعد الترميز
feature_columns_encoded = [col for col in data_encoded.columns if col not in exclude_columns]

# إعادة تقسيم البيانات بعد الترميز
train_data_encoded = data_encoded[data_encoded['MapDate'] <= split_date]
test_data_encoded = data_encoded[data_encoded['MapDate'] > split_date]

# تحضير البيانات
X_train = train_data_encoded[feature_columns_encoded]
X_test = test_data_encoded[feature_columns_encoded]

# تطبيع البيانات
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# قاموس لتخزين نتائج النماذج
models_results = {}

# دالة لتدريب وتقييم النموذج
def train_evaluate_model(model, model_name, X_train, X_test, y_train, y_test, target_name):
    # تدريب النموذج
    model.fit(X_train, y_train)
    
    # التنبؤ
    y_pred = model.predict(X_test)
    
    # حساب مقاييس الأداء
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return {
        'model': model,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'predictions': y_pred
    }

# تدريب نماذج مختلفة لكل مستوى من مستويات الجفاف
for target in target_columns:
    print(f"\nتدريب النماذج للتنبؤ بـ {target}:")
    
    y_train = train_data[target]
    y_test = test_data[target]
    
    # نموذج الانحدار الخطي
    lr_model = LinearRegression()
    lr_results = train_evaluate_model(lr_model, 'Linear Regression', 
                                     X_train_scaled, X_test_scaled, 
                                     y_train, y_test, target)
    
    # نموذج الغابات العشوائية
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_results = train_evaluate_model(rf_model, 'Random Forest', 
                                     X_train_scaled, X_test_scaled, 
                                     y_train, y_test, target)
    
    # نموذج XGBoost
    xgb_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    xgb_results = train_evaluate_model(xgb_model, 'XGBoost', 
                                      X_train_scaled, X_test_scaled, 
                                      y_train, y_test, target)
    
    # نموذج Gradient Boosting
    gb_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    gb_results = train_evaluate_model(gb_model, 'Gradient Boosting', 
                                     X_train_scaled, X_test_scaled, 
                                     y_train, y_test, target)
    
    # تخزين النتائج
    models_results[target] = {
        'Linear Regression': lr_results,
        'Random Forest': rf_results,
        'XGBoost': xgb_results,
        'Gradient Boosting': gb_results
    }
    
    # عرض نتائج النماذج
    print(f"نتائج النماذج للتنبؤ بـ {target}:")
    print(f"الانحدار الخطي - RMSE: {lr_results['rmse']:.4f}, MAE: {lr_results['mae']:.4f}, R²: {lr_results['r2']:.4f}")
    print(f"الغابات العشوائية - RMSE: {rf_results['rmse']:.4f}, MAE: {rf_results['mae']:.4f}, R²: {rf_results['r2']:.4f}")
    print(f"XGBoost - RMSE: {xgb_results['rmse']:.4f}, MAE: {xgb_results['mae']:.4f}, R²: {xgb_results['r2']:.4f}")
    print(f"Gradient Boosting - RMSE: {gb_results['rmse']:.4f}, MAE: {gb_results['mae']:.4f}, R²: {gb_results['r2']:.4f}")

# 7. تحسين النموذج الأفضل (XGBoost)
print("\n=== 7. تحسين النموذج الأفضل (XGBoost) ===")

# تحديد أفضل معلمات لنموذج XGBoost
best_models = {}

for target in target_columns:
    print(f"\nتحسين نموذج XGBoost للتنبؤ بـ {target}:")
    
    y_train = train_data[target]
    y_test = test_data[target]
    
    # تحديد نطاق المعلمات - تقليل عدد الاحتمالات لتسريع العملية
    param_grid = {
        'n_estimators': [100],
        'max_depth': [3, 5],
        'learning_rate': [0.05, 0.1],
        'subsample': [0.8, 1.0]
    }
    
    # استخدام البحث الشبكي مع التحقق المتقاطع الزمني
    tscv = TimeSeriesSplit(n_splits=3)
    
    xgb_model = xgb.XGBRegressor(random_state=42)
    grid_search = GridSearchCV(
        estimator=xgb_model,
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_mean_squared_error',
        n_jobs=-1,
        verbose=0
    )
    
    grid_search.fit(X_train_scaled, y_train)
    
    # أفضل معلمات
    best_params = grid_search.best_params_
    print(f"أفضل معلمات: {best_params}")
    
    # تدريب النموذج باستخدام أفضل المعلمات
    best_model = xgb.XGBRegressor(**best_params, random_state=42)
    best_model.fit(X_train_scaled, y_train)
    
    # تقييم النموذج المحسن
    y_pred = best_model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"أداء النموذج المحسن - RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")
    
    # تخزين النموذج المحسن
    best_models[target] = {
        'model': best_model,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'predictions': y_pred
    }

# 8. تصور النتائج
print("\n=== 8. تصور النتائج ===")

# رسم النتائج الفعلية مقابل التنبؤات
plt.figure(figsize=(15, 10))
for i, target in enumerate(target_columns):
    plt.subplot(2, 3, i+1)
    
    # الحصول على التنبؤات من النموذج المحسن
    y_test = test_data[target]
    y_pred = best_models[target]['predictions']
    
    # رسم القيم الفعلية والتنبؤات
    plt.plot(test_data['MapDate'], y_test, label='القيم الفعلية', color='blue')
    plt.plot(test_data['MapDate'], y_pred, label='التنبؤات', color='red', linestyle='--')
    
    plt.title(f'القيم الفعلية مقابل التنبؤات لـ {target}')
    plt.xlabel('التاريخ')
    plt.ylabel('النسبة المئوية')
    plt.legend()
    plt.grid(True)
    
    # إضافة مقاييس الأداء إلى الرسم
    rmse = best_models[target]['rmse']
    r2 = best_models[target]['r2']
    plt.annotate(f'RMSE: {rmse:.4f}\nR²: {r2:.4f}', 
                xy=(0.05, 0.85), xycoords='axes fraction')

plt.tight_layout()
plt.savefig('predictions_vs_actual.png')
plt.close()

# 9. أهمية المتغيرات
print("\n=== 9. أهمية المتغيرات ===")

# تحليل أهمية المتغيرات لكل نموذج
plt.figure(figsize=(15, 10))
for i, target in enumerate(target_columns):
    plt.subplot(2, 3, i+1)
    
    # الحصول على أهمية المتغيرات
    model = best_models[target]['model']
    importance = model.feature_importances_
    
    # ترتيب المتغيرات حسب الأهمية
    indices = np.argsort(importance)[-10:]  # أهم 10 متغيرات
    
    # رسم أهمية المتغيرات
    plt.barh(range(len(indices)), importance[indices])
    plt.yticks(range(len(indices)), [feature_columns_encoded[j] for j in indices])
    plt.title(f'أهم المتغيرات للتنبؤ بـ {target}')
    plt.xlabel('الأهمية')
    
plt.tight_layout()
plt.savefig('feature_importance.png')
plt.close()

print("\n=== تم الانتهاء من بناء وتقييم النماذج ===")
print("تم حفظ الرسومات البيانية في ملفات PNG")

# 10. ملخص النتائج
print("\n=== 10. ملخص النتائج ===")
print("أداء النماذج المحسنة:")

for target in target_columns:
    rmse = best_models[target]['rmse']
    mae = best_models[target]['mae']
    r2 = best_models[target]['r2']
    print(f"{target} - RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")

print("\nتم بناء نماذج تنبؤية لمستويات الجفاف المختلفة (D0-D4) باستخدام XGBoost المحسن.")
print("النماذج تستخدم بيانات تاريخية وتحليل الاتجاهات الزمنية للتنبؤ بمستويات الجفاف المستقبلية.")
print("تم تحسين النماذج باستخدام البحث الشبكي وتحقق متقاطع زمني للحصول على أفضل أداء.")

# 11. تقييم إضافي للنموذج لتجنب مشاكل Overfitting و Underfitting
print("\n=== 11. تقييم إضافي للنموذج لتجنب مشاكل Overfitting و Underfitting ===")

from sklearn.model_selection import learning_curve
import pickle
import os

# إنشاء مجلد للنماذج إذا لم يكن موجودًا
if not os.path.exists('models'):
    os.makedirs('models')

# تقييم منحنى التعلم لكل نموذج للتحقق من مشاكل Overfitting و Underfitting
for target in target_columns:
    print(f"\nتقييم منحنى التعلم للنموذج {target}:")
    
    # الحصول على النموذج المحسن
    best_model = best_models[target]['model']
    
    # حساب منحنى التعلم
    train_sizes, train_scores, test_scores = learning_curve(
        best_model, X_train_scaled, train_data[target],
        cv=TimeSeriesSplit(n_splits=5),
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring='neg_mean_squared_error',
        n_jobs=-1
    )
    
    # حساب متوسط وانحراف معياري لدرجات التدريب والاختبار
    train_mean = -np.mean(train_scores, axis=1)
    train_std = np.std(train_scores, axis=1)
    test_mean = -np.mean(test_scores, axis=1)
    test_std = np.std(test_scores, axis=1)
    
    # تحليل منحنى التعلم
    gap = test_mean[-1] - train_mean[-1]
    train_score_improvement = train_mean[0] - train_mean[-1]
    
    print(f"الفجوة بين أداء التدريب والاختبار: {gap:.4f}")
    print(f"تحسن أداء التدريب من بداية التدريب إلى نهايته: {train_score_improvement:.4f}")
    
    if gap > 0.2 * test_mean[-1]:
        print("تحذير: قد يكون هناك Overfitting. النموذج يؤدي بشكل أفضل بكثير على بيانات التدريب مقارنة ببيانات الاختبار.")
        # تعديل معلمات النموذج لتقليل Overfitting
        print("تعديل معلمات النموذج لتقليل Overfitting...")
        
        # زيادة قيمة regularization أو تقليل عمق الشجرة
        updated_params = best_model.get_params()
        if 'max_depth' in updated_params and updated_params['max_depth'] > 3:
            updated_params['max_depth'] -= 1
        if 'reg_alpha' in updated_params and updated_params['reg_alpha'] is not None:
            updated_params['reg_alpha'] *= 1.5
        else:
            updated_params['reg_alpha'] = 0.1
        if 'reg_lambda' in updated_params and updated_params['reg_lambda'] is not None:
            updated_params['reg_lambda'] *= 1.5
        else:
            updated_params['reg_lambda'] = 0.1
            
        # إعادة تدريب النموذج بالمعلمات المحدثة
        best_model.set_params(**updated_params)
        best_model.fit(X_train_scaled, train_data[target])
        
        # إعادة تقييم النموذج
        y_pred = best_model.predict(X_test_scaled)
        rmse = np.sqrt(mean_squared_error(test_data[target], y_pred))
        r2 = r2_score(test_data[target], y_pred)
        print(f"أداء النموذج بعد التعديل - RMSE: {rmse:.4f}, R²: {r2:.4f}")
        
        # تحديث النموذج في القاموس
        best_models[target]['model'] = best_model
        best_models[target]['rmse'] = rmse
        best_models[target]['r2'] = r2
        best_models[target]['predictions'] = y_pred
        
    elif train_score_improvement < 0.1 * train_mean[0]:
        print("تحذير: قد يكون هناك Underfitting. النموذج لم يتعلم بشكل كافٍ من بيانات التدريب.")
        # تعديل معلمات النموذج لتقليل Underfitting
        print("تعديل معلمات النموذج لتقليل Underfitting...")
        
        # زيادة تعقيد النموذج
        updated_params = best_model.get_params()
        if 'max_depth' in updated_params:
            updated_params['max_depth'] += 1
        if 'n_estimators' in updated_params:
            updated_params['n_estimators'] = min(updated_params['n_estimators'] + 50, 300)
            
        # إعادة تدريب النموذج بالمعلمات المحدثة
        best_model.set_params(**updated_params)
        best_model.fit(X_train_scaled, train_data[target])
        
        # إعادة تقييم النموذج
        y_pred = best_model.predict(X_test_scaled)
        rmse = np.sqrt(mean_squared_error(test_data[target], y_pred))
        r2 = r2_score(test_data[target], y_pred)
        print(f"أداء النموذج بعد التعديل - RMSE: {rmse:.4f}, R²: {r2:.4f}")
        
        # تحديث النموذج في القاموس
        best_models[target]['model'] = best_model
        best_models[target]['rmse'] = rmse
        best_models[target]['r2'] = r2
        best_models[target]['predictions'] = y_pred
    else:
        print("النموذج متوازن جيدًا بين Overfitting و Underfitting.")
    
    # حفظ النموذج النهائي بصيغة pkl
    model_filename = f'models/{target}_best_model.pkl'
    with open(model_filename, 'wb') as file:
        pickle.dump(best_model, file)
    
    # حفظ المعلومات الإضافية للنموذج
    model_info_filename = f'models/{target}_model_info.pkl'
    model_info = {
        'feature_columns': feature_columns_encoded,
        'scaler': scaler,
        'performance': {
            'rmse': best_models[target]['rmse'],
            'mae': best_models[target]['mae'],
            'r2': best_models[target]['r2']
        },
        'parameters': best_model.get_params()
    }
    with open(model_info_filename, 'wb') as file:
        pickle.dump(model_info, file)
    
    print(f"تم حفظ النموذج النهائي في {model_filename}")
    print(f"تم حفظ معلومات النموذج في {model_info_filename}")

print("\n=== تم الانتهاء من تقييم وحفظ النماذج ===")
print("تم حفظ جميع النماذج المحسنة بصيغة pkl في مجلد 'models'")
print("يمكن استخدام هذه النماذج للتنبؤ بمستويات الجفاف المستقبلية")

# قاموس لتخزين نتائج النماذج
models_results = {}

# دالة لتدريب وتقييم النموذج
def train_evaluate_model(model, model_name, X_train, X_test, y_train, y_test, target_name):
    # تدريب النموذج
    model.fit(X_train, y_train)
    
    # التنبؤ
    y_pred = model.predict(X_test)
    
    # حساب مقاييس الأداء
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    return {
        'model': model,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'predictions': y_pred
    }

# تدريب نماذج مختلفة لكل مستوى من مستويات الجفاف
for target in target_columns:
    print(f"\nتدريب النماذج للتنبؤ بـ {target}:")
    
    y_train = train_data[target]
    y_test = test_data[target]
    
    # نموذج الانحدار الخطي
    lr_model = LinearRegression()
    lr_results = train_evaluate_model(lr_model, 'Linear Regression', 
                                     X_train_scaled, X_test_scaled, 
                                     y_train, y_test, target)
    
    # نموذج الغابات العشوائية
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_results = train_evaluate_model(rf_model, 'Random Forest', 
                                     X_train_scaled, X_test_scaled, 
                                     y_train, y_test, target)
    
    # نموذج XGBoost
    xgb_model = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    xgb_results = train_evaluate_model(xgb_model, 'XGBoost', 
                                      X_train_scaled, X_test_scaled, 
                                      y_train, y_test, target)
    
    # نموذج Gradient Boosting
    gb_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
    gb_results = train_evaluate_model(gb_model, 'Gradient Boosting', 
                                     X_train_scaled, X_test_scaled, 
                                     y_train, y_test, target)
    
    # تخزين النتائج
    models_results[target] = {
        'Linear Regression': lr_results,
        'Random Forest': rf_results,
        'XGBoost': xgb_results,
        'Gradient Boosting': gb_results
    }
    
    # عرض نتائج النماذج
    print(f"نتائج النماذج للتنبؤ بـ {target}:")
    print(f"الانحدار الخطي - RMSE: {lr_results['rmse']:.4f}, MAE: {lr_results['mae']:.4f}, R²: {lr_results['r2']:.4f}")
    print(f"الغابات العشوائية - RMSE: {rf_results['rmse']:.4f}, MAE: {rf_results['mae']:.4f}, R²: {rf_results['r2']:.4f}")
    print(f"XGBoost - RMSE: {xgb_results['rmse']:.4f}, MAE: {xgb_results['mae']:.4f}, R²: {xgb_results['r2']:.4f}")
    print(f"Gradient Boosting - RMSE: {gb_results['rmse']:.4f}, MAE: {gb_results['mae']:.4f}, R²: {gb_results['r2']:.4f}")

# 7. تحسين النموذج الأفضل (XGBoost)
print("\n=== 7. تحسين النموذج الأفضل (XGBoost) ===")

# تحديد أفضل معلمات لنموذج XGBoost
best_models = {}

for target in target_columns:
    print(f"\nتحسين نموذج XGBoost للتنبؤ بـ {target}:")
    
    y_train = train_data[target]
    y_test = test_data[target]
    
    # تحديد نطاق المعلمات
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.05, 0.1],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0]
    }
    
    # استخدام البحث الشبكي مع التحقق المتقاطع الزمني
    tscv = TimeSeriesSplit(n_splits=5)
    
    xgb_model = xgb.XGBRegressor(random_state=42)
    grid_search = GridSearchCV(
        estimator=xgb_model,
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_mean_squared_error',
        n_jobs=-1,
        verbose=0
    )
    
    grid_search.fit(X_train_scaled, y_train)
    
    # أفضل معلمات
    best_params = grid_search.best_params_
    print(f"أفضل معلمات: {best_params}")
    
    # تدريب النموذج باستخدام أفضل المعلمات
    best_model = xgb.XGBRegressor(**best_params, random_state=42)
    best_model.fit(X_train_scaled, y_train)
    
    # تقييم النموذج المحسن
    y_pred = best_model.predict(X_test_scaled)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"أداء النموذج المحسن - RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")
    
    # تخزين النموذج المحسن
    best_models[target] = {
        'model': best_model,
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'predictions': y_pred
    }

# 8. تصور النتائج
print("\n=== 8. تصور النتائج ===")

# رسم النتائج الفعلية مقابل التنبؤات
plt.figure(figsize=(15, 10))
for i, target in enumerate(target_columns):
    plt.subplot(2, 3, i+1)
    
    # الحصول على التنبؤات من النموذج المحسن
    y_test = test_data[target]
    y_pred = best_models[target]['predictions']
    
    # رسم القيم الفعلية والتنبؤات
    plt.plot(test_data['MapDate'], y_test, label='القيم الفعلية', color='blue')
    plt.plot(test_data['MapDate'], y_pred, label='التنبؤات', color='red', linestyle='--')
    
    plt.title(f'القيم الفعلية مقابل التنبؤات لـ {target}')
    plt.xlabel('التاريخ')
    plt.ylabel('النسبة المئوية')
    plt.legend()
    plt.grid(True)
    
    # إضافة مقاييس الأداء إلى الرسم
    rmse = best_models[target]['rmse']
    r2 = best_models[target]['r2']
    plt.annotate(f'RMSE: {rmse:.4f}\nR²: {r2:.4f}', 
                xy=(0.05, 0.85), xycoords='axes fraction')

plt.tight_layout()
plt.savefig('predictions_vs_actual.png')
plt.close()

# 9. أهمية المتغيرات
print("\n=== 9. أهمية المتغيرات ===")

# تحليل أهمية المتغيرات لكل نموذج
plt.figure(figsize=(15, 10))
for i, target in enumerate(target_columns):
    plt.subplot(2, 3, i+1)
    
    # الحصول على أهمية المتغيرات
    model = best_models[target]['model']
    importance = model.feature_importances_
    
    # ترتيب المتغيرات حسب الأهمية
    indices = np.argsort(importance)[-15:]  # أهم 15 متغير
    
    # رسم أهمية المتغيرات
    plt.barh(range(len(indices)), importance[indices])
    plt.yticks(range(len(indices)), [feature_columns_encoded[j] for j in indices])
    plt.title(f'أهم المتغيرات للتنبؤ بـ {target}')
    plt.xlabel('الأهمية')
    
plt.tight_layout()
plt.savefig('feature_importance.png')
plt.close()

print("\n=== تم الانتهاء من بناء وتقييم النماذج ===")
print("تم حفظ الرسومات البيانية في ملفات PNG")

# 10. ملخص النتائج
print("\n=== 10. ملخص النتائج ===")
print("أداء النماذج المحسنة:")

for target in target_columns:
    rmse = best_models[target]['rmse']
    mae = best_models[target]['mae']
    r2 = best_models[target]['r2']
    print(f"{target} - RMSE: {rmse:.4f}, MAE: {mae:.4f}, R²: {r2:.4f}")

print("\nتم بناء نماذج تنبؤية لمستويات الجفاف المختلفة (D0-D4) باستخدام XGBoost المحسن.")
print("النماذج تستخدم بيانات تاريخية وتحليل الاتجاهات الزمنية للتنبؤ بمستويات الجفاف المستقبلية.")
print("تم تحسين النماذج باستخدام البحث الشبكي وتحقق متقاطع زمني للحصول على أفضل أداء.")