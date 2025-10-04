import os
import re
import numpy as np
import rasterio
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import glob
import folium
from folium.plugins import TimestampedGeoJson
import branca.colormap as cm
import geopandas as gpd
from rasterio.warp import transform_bounds
from pyproj import Transformer
import torch
from torch import nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import pickle
import matplotlib.colors as mcolors

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Path to TIFF folder
tiff_folder = r"d:\nasa\NDVI\Historical Tiff"

# Get list of all NDVI TIFF files (exclude VI_Quality files)
tiff_files = [f for f in glob.glob(os.path.join(tiff_folder, "*.tif")) if "NDVI" in f and "Quality" not in f]

# Extract dates from filenames
dates = []
ndvi_arrays = []
file_paths = []

print("Reading NDVI files...")
for tiff_file in tqdm(tiff_files):
    filename = os.path.basename(tiff_file)

    # Search for date format in name (doyYYYYDDD or AYYYYDDD)
    match = re.search(r'(?:doy|A)(\d{4})(\d{3})', filename)
    if not match:
        print(f"⚠️ Skipping {filename}: Date not found")
        continue

    year = int(match.group(1))
    day_of_year = int(match.group(2))

    # Validate day
    if day_of_year < 1 or day_of_year > 366:
        print(f"⚠️ Skipping {filename}: Invalid day {day_of_year}")
        continue

    # Convert day to date
    date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
    
    # Read NDVI data
    try:
        with rasterio.open(tiff_file) as src:
            ndvi = src.read(1)  # Read first band
            
            # Save projection and transform info
            if len(ndvi_arrays) == 0:
                transform = src.transform
                crs = src.crs
                bounds = src.bounds
                
            dates.append(date)
            ndvi_arrays.append(ndvi)
            file_paths.append(tiff_file)
            
            print(f"✅ Read {filename}, Date: {date.strftime('%Y-%m-%d')}")
    except Exception as e:
        print(f"❌ Error reading {filename}: {str(e)}")

# Convert lists to NumPy arrays
dates = np.array(dates)
ndvi_arrays = np.array(ndvi_arrays)

print(f"\n📊 Read {len(ndvi_arrays)} NDVI images")
print(f"Data shape: {ndvi_arrays.shape}")

# Function to convert image coordinates to geographic coordinates
def get_geo_bounds(bounds, src_crs):
    # Convert from project coordinates to geographic coordinates (longitude/latitude)
    transformer = Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
    minx, miny = transformer.transform(bounds.left, bounds.bottom)
    maxx, maxy = transformer.transform(bounds.right, bounds.top)
    return minx, miny, maxx, maxy

# Function to properly scale NDVI values
def scale_ndvi(ndvi_array):
    """
    Scale NDVI values from their original range (-3000 to 10000) to actual NDVI range (-1 to 1)
    MODIS NDVI data is stored as int16 with a scale factor of 0.0001
    """
    ndvi_clean = ndvi_array.copy().astype(np.float32)
    
    # Replace NoData values with NaN
    # MODIS NDVI NoData value is typically -3000
    ndvi_clean[ndvi_clean <= -3000] = np.nan
    
    # Apply scale factor to convert to actual NDVI values
    # MODIS NDVI data is stored with a scale factor of 0.0001
    valid_mask = ~np.isnan(ndvi_clean)
    ndvi_clean[valid_mask] = ndvi_clean[valid_mask] * 0.0001
    
    # Additional data cleaning: clip to valid NDVI range (-1 to 1)
    ndvi_clean[ndvi_clean < -1] = -1
    ndvi_clean[ndvi_clean > 1] = 1
    
    # Print statistics for debugging
    if valid_mask.any():
        print(f"NDVI stats - Min: {np.nanmin(ndvi_clean):.4f}, Max: {np.nanmax(ndvi_clean):.4f}, Mean: {np.nanmean(ndvi_clean):.4f}")
    
    return ndvi_clean

# Process all NDVI arrays to correct scale
scaled_ndvi_arrays = []
for ndvi in ndvi_arrays:
    scaled_ndvi = scale_ndvi(ndvi)
    scaled_ndvi_arrays.append(scaled_ndvi)

scaled_ndvi_arrays = np.array(scaled_ndvi_arrays)

# Create PyTorch dataset
class NDVIDataset(Dataset):
    def __init__(self, ndvi_arrays, dates, transform=None):
        # Store the properly scaled NDVI data
        self.ndvi_data = []
        for ndvi in ndvi_arrays:
            # Replace NaN with 0 after scaling
            ndvi_clean = np.nan_to_num(ndvi, nan=0)
            self.ndvi_data.append(ndvi_clean)
            
        self.ndvi_data = np.array(self.ndvi_data)
        
        # Extract time features (year, month, day of year)
        self.time_features = np.array([
            [date.year, date.month, date.timetuple().tm_yday] 
            for date in dates
        ], dtype=np.float32)
        
        # Normalize time features
        self.time_features[:, 0] = (self.time_features[:, 0] - 2014) / 11  # Years from 2014 to 2025
        self.time_features[:, 1] = (self.time_features[:, 1] - 1) / 11  # Months from 1 to 12
        self.time_features[:, 2] = (self.time_features[:, 2] - 1) / 365  # Days from 1 to 366
        
        self.transform = transform
        
    def __len__(self):
        return len(self.ndvi_data) - 1  # Use each image as input and the next image as target
        
    def __getitem__(self, idx):
        x_ndvi = self.ndvi_data[idx]
        y_ndvi = self.ndvi_data[idx + 1]
        
        x_time = self.time_features[idx]
        
        if self.transform:
            x_ndvi = self.transform(x_ndvi)
            y_ndvi = self.transform(y_ndvi)
            
        # Reshape data to fit neural network
        x_ndvi = x_ndvi.reshape(1, x_ndvi.shape[0], x_ndvi.shape[1])
        
        return {
            'ndvi': torch.tensor(x_ndvi, dtype=torch.float32),
            'time': torch.tensor(x_time, dtype=torch.float32),
            'target': torch.tensor(y_ndvi, dtype=torch.float32)
        }

# Define improved CNN model with batch normalization and skip connections
class ImprovedNDVIModel(nn.Module):
    def __init__(self, input_channels=1, time_features=3):
        super(ImprovedNDVIModel, self).__init__()
        
        # NDVI processing with convolutional layers
        self.conv1 = nn.Conv2d(input_channels, 16, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(16)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(32)
        self.conv3 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(64)
        self.conv4 = nn.Conv2d(64, 32, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(32)
        self.conv5 = nn.Conv2d(32, 16, kernel_size=3, padding=1)
        self.bn5 = nn.BatchNorm2d(16)
        self.conv6 = nn.Conv2d(16, 1, kernel_size=3, padding=1)
        
        # Time data processing
        self.time_fc1 = nn.Linear(time_features, 64)
        self.time_bn1 = nn.BatchNorm1d(64)
        self.time_fc2 = nn.Linear(64, 128)
        self.time_bn2 = nn.BatchNorm1d(128)
        
        # Attention mechanism for time features
        self.attention = nn.Linear(128, 1)
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        
    def forward(self, ndvi, time):
        # Process NDVI data with skip connections
        x1 = self.relu(self.bn1(self.conv1(ndvi)))
        x2 = self.relu(self.bn2(self.conv2(x1)))
        x3 = self.relu(self.bn3(self.conv3(x2)))
        x4 = self.relu(self.bn4(self.conv4(x3))) + x2  # Skip connection
        x5 = self.relu(self.bn5(self.conv5(x4))) + x1  # Skip connection
        x_ndvi = self.conv6(x5)
        
        # Process time data
        x_time = self.relu(self.time_bn1(self.time_fc1(time)))
        x_time = self.dropout(x_time)
        x_time = self.relu(self.time_bn2(self.time_fc2(x_time)))
        
        # We return the processed NDVI data as final output
        # Time data can be used to modify outputs in future versions
        return x_ndvi

# Function to train the model
def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=15):
    model.to(device)
    best_val_loss = float('inf')
    train_losses = []
    val_losses = []
    
    for epoch in range(num_epochs):
        # Training
        model.train()
        train_loss = 0.0
        
        for batch in tqdm(train_loader, desc=f"Training - Epoch {epoch+1}/{num_epochs}"):
            ndvi = batch['ndvi'].to(device)
            time = batch['time'].to(device)
            target = batch['target'].to(device)
            
            optimizer.zero_grad()
            output = model(ndvi, time)
            loss = criterion(output.squeeze(), target)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        train_losses.append(train_loss)
        
        # Validation
        model.eval()
        val_loss = 0.0
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc=f"Validation - Epoch {epoch+1}/{num_epochs}"):
                ndvi = batch['ndvi'].to(device)
                time = batch['time'].to(device)
                target = batch['target'].to(device)
                
                output = model(ndvi, time)
                loss = criterion(output.squeeze(), target)
                
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        val_losses.append(val_loss)
        
        print(f"Epoch {epoch+1}/{num_epochs}, Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), 'best_ndvi_model.pth')
            print(f"Saved best model with validation loss: {val_loss:.4f}")
    
    return train_losses, val_losses

# Classify NDVI values into vegetation health categories
def classify_ndvi_health(ndvi_array):
    """
    Classify NDVI values into vegetation health categories
    NDVI ranges:
    - < 0: Water/clouds
    - 0-0.2: Barren/degraded
    - 0.2-0.4: Medium health
    - > 0.4: Healthy vegetation
    """
    # Create classification array (0: degraded, 1: medium, 2: healthy)
    health_class = np.zeros_like(ndvi_array, dtype=np.uint8)
    
    # Classify values with more realistic thresholds for urban/semi-urban areas
    # < 0: Water/clouds (keep as 0)
    # 0-0.15: Barren/degraded (0)
    # 0.15-0.3: Medium health (1)
    # > 0.3: Healthy vegetation (2)
    health_class[(ndvi_array >= 0.15) & (ndvi_array < 0.3)] = 1
    health_class[ndvi_array >= 0.3] = 2
    
    # Count pixels in each category for validation
    total_valid = np.sum(~np.isnan(ndvi_array))
    if total_valid > 0:
        degraded_count = np.sum((ndvi_array >= 0) & (ndvi_array < 0.15))
        medium_count = np.sum((ndvi_array >= 0.15) & (ndvi_array < 0.3))
        healthy_count = np.sum(ndvi_array >= 0.3)
        
        print(f"Vegetation health distribution:")
        print(f"  - Degraded: {degraded_count/total_valid*100:.1f}%")
        print(f"  - Medium: {medium_count/total_valid*100:.1f}%")
        print(f"  - Healthy: {healthy_count/total_valid*100:.1f}%")
    
    # Replace NaN with 255 (special value for missing data)
    health_class[np.isnan(ndvi_array)] = 255
    
    return health_class

# Create interactive map
def create_interactive_map(ndvi_arrays, dates, bounds, crs):
    # Convert image bounds to geographic coordinates
    minx, miny, maxx, maxy = get_geo_bounds(bounds, crs)
    
    # Create folium map
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='CartoDB positron')
    
    # Create colormap
    colormap = cm.LinearColormap(
        colors=['brown', 'yellow', 'green'],
        vmin=0, vmax=2,
        caption='Vegetation Health'
    )
    colormap.add_to(m)
    
    # Create custom colormap for matplotlib
    cmap = mcolors.ListedColormap(['brown', 'yellow', 'green'])
    bounds = [0, 1, 2, 3]
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    # Add layers for each date
    for i, (ndvi, date) in enumerate(zip(ndvi_arrays, dates)):
        # Classify NDVI into health categories
        health_class = classify_ndvi_health(ndvi)
        
        # Convert to matplotlib image
        plt.figure(figsize=(10, 8))
        plt.imshow(health_class, cmap=cmap, norm=norm, interpolation='nearest')
        plt.axis('off')
        plt.colorbar(ticks=[0.5, 1.5, 2.5], 
                    label='Vegetation Health', 
                    orientation='vertical')
        plt.annotate('Degraded', (0, 0.5), xycoords='axes fraction', color='white')
        plt.annotate('Medium', (0, 1.5), xycoords='axes fraction', color='black')
        plt.annotate('Healthy', (0, 2.5), xycoords='axes fraction', color='white')
        plt.title(f'Vegetation Health on {date.strftime("%Y-%m-%d")}')
        
        # Save image
        img_path = f'ndvi_health_{date.strftime("%Y%m%d")}.png'
        plt.savefig(img_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # Add image as layer to map
        image_overlay = folium.raster_layers.ImageOverlay(
            image=img_path,
            bounds=[[miny, minx], [maxy, maxx]],
            opacity=0.7,
            name=f'NDVI {date.strftime("%Y-%m-%d")}',
            overlay=True,
            control=True,
            show=i == len(ndvi_arrays) - 1  # Show most recent image
        )
        image_overlay.add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save map
    m.save('ndvi_interactive_map.html')
    print("Created interactive map: ndvi_interactive_map.html")
    
    return m

# Export model to PKI format
def export_model_to_pki(model, filename='ndvi_model.pki'):
    # Save model using pickle
    with open(filename, 'wb') as f:
        pickle.dump(model, f)
    print(f"Exported model to: {filename}")

# Main function
def main():
    # Split data into training and validation sets
    if len(scaled_ndvi_arrays) > 1:
        # Create dataset
        dataset = NDVIDataset(scaled_ndvi_arrays, dates)
        
        # Split data
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False)
        
        # Create model
        model = ImprovedNDVIModel()
        
        # Define loss function and optimizer
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
        
        # Train model
        print("Starting model training...")
        train_losses, val_losses = train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=15)
        
        # Export model
        export_model_to_pki(model)
        
        # Plot loss curve
        plt.figure(figsize=(10, 6))
        plt.plot(train_losses, label='Training Loss')
        plt.plot(val_losses, label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.title('Training Loss Curve')
        plt.legend()
        plt.savefig('training_loss.png')
        plt.close()
    
    # Create interactive map
    print("Creating interactive map...")
    with rasterio.open(file_paths[0]) as src:
        bounds = src.bounds
        crs = src.crs
    
    create_interactive_map(scaled_ndvi_arrays, dates, bounds, crs)
    
    # Display example of NDVI data
    plt.figure(figsize=(12, 10))
    
    # Find a good example image (not too many NaN values)
    for i, ndvi in enumerate(scaled_ndvi_arrays):
        if np.isnan(ndvi).sum() / ndvi.size < 0.3:  # Less than 30% NaN values
            example_idx = i
            break
    else:
        example_idx = 0  # Default to first image if all have many NaNs
    
    example_ndvi = scaled_ndvi_arrays[example_idx]
    example_date = dates[example_idx]
    
    # Create a masked array for better visualization
    masked_ndvi = np.ma.masked_invalid(example_ndvi)
    
    # Plot NDVI values
    plt.subplot(1, 2, 1)
    im = plt.imshow(masked_ndvi, cmap='RdYlGn', vmin=-0.2, vmax=1.0)
    plt.colorbar(im, label='NDVI Value')
    plt.title(f'NDVI Values on {example_date.strftime("%Y-%m-%d")}')
    
    # Plot vegetation health classification
    plt.subplot(1, 2, 2)
    health_class = classify_ndvi_health(example_ndvi)
    health_cmap = mcolors.ListedColormap(['brown', 'yellow', 'green'])
    health_bounds = [0, 1, 2, 3]
    health_norm = mcolors.BoundaryNorm(health_bounds, health_cmap.N)
    
    im2 = plt.imshow(health_class, cmap=health_cmap, norm=health_norm)
    cbar = plt.colorbar(im2, ticks=[0.5, 1.5, 2.5])
    cbar.ax.set_yticklabels(['Degraded', 'Medium', 'Healthy'])
    plt.title(f'Vegetation Health on {example_date.strftime("%Y-%m-%d")}')
    
    plt.tight_layout()
    plt.savefig('ndvi_example.png', dpi=150)
    plt.close()
    
    print("Analysis complete!")

if __name__ == "__main__":
    main()