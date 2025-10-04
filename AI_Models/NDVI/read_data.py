import os
import re
import numpy as np
import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import glob

# Path to the images folder
tiff_folder = r"d:\nasa\NDVI\Historical Tiff"

# Get a list of all TIFF files
tiff_files = glob.glob(os.path.join(tiff_folder, "*.tif"))

# Extract dates from filenames
dates = []
ndvi_arrays = []

for tiff_file in tiff_files:
    filename = os.path.basename(tiff_file)

    # ابحث عن صيغة التاريخ في الاسم (doyYYYYDDD أو AYYYYDDD)
    match = re.search(r'(?:doy|A)(\d{4})(\d{3})', filename)
    if not match:
        print(f"⚠️ Skipping {filename}: no date found")
        continue

    year = int(match.group(1))
    day_of_year = int(match.group(2))

    # تحقق من اليوم
    if day_of_year < 1 or day_of_year > 366:
        print(f"⚠️ Skipping {filename}: invalid day_of_year {day_of_year}")
        continue

    # تحويل اليوم لتاريخ
    date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
    dates.append(date)

    # قراءة بيانات NDVI
    with rasterio.open(tiff_file) as src:
        ndvi = src.read(1)  # Read the first band
        ndvi_arrays.append(ndvi)

    print(f"✅ Read {filename}, Date: {date.strftime('%Y-%m-%d')}")

# Convert lists to NumPy arrays
dates = np.array(dates)
ndvi_arrays = np.array(ndvi_arrays)

print(f"\n📊 Read {len(ndvi_arrays)} NDVI images")
print(f"Data shape: {ndvi_arrays.shape}")

# Display an example NDVI image
if len(ndvi_arrays) > 0:
    plt.figure(figsize=(10, 8))
    plt.imshow(ndvi_arrays[0], cmap='RdYlGn')
    plt.colorbar(label='NDVI')
    plt.title(f'NDVI on {dates[0].strftime("%Y-%m-%d")}')
    plt.show()

# Calculate mean NDVI for each image
mean_ndvi = np.array([np.mean(ndvi[ndvi != -3000]) for ndvi in ndvi_arrays])  # Exclude NoData values

# Plot time series of the mean
plt.figure(figsize=(12, 6))
plt.plot(dates, mean_ndvi)
plt.title('Mean NDVI Over Time')
plt.xlabel('Date')
plt.ylabel('Mean NDVI')
plt.grid(True)
plt.show()

# Analyze seasonal changes
years = np.array([date.year for date in dates])
months = np.array([date.month for date in dates])

# Calculate mean NDVI by month
monthly_ndvi = {}
for year in np.unique(years):
    for month in range(1, 13):
        mask = (years == year) & (months == month)
        if np.any(mask):
            if month not in monthly_ndvi:
                monthly_ndvi[month] = []
            monthly_ndvi[month].extend(mean_ndvi[mask])

# Plot monthly mean NDVI
months_names = ['January', 'February', 'March', 'April', 'May', 'June', 
                'July', 'August', 'September', 'October', 'November', 'December']
monthly_means = [np.mean(monthly_ndvi.get(m+1, [0])) for m in range(12)]

plt.figure(figsize=(10, 6))
plt.bar(months_names, monthly_means)
plt.title('Monthly Mean NDVI')
plt.ylabel('Mean NDVI')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
