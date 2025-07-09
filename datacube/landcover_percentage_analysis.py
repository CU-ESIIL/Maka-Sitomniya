#!/usr/bin/env python3
"""
Land Cover Percentage vs Temperature Change Analysis

For each land cover type, create scatter plots showing:
X-axis: Percentage of that land cover within each temperature pixel
Y-axis: Temperature change for that pixel

This reveals how different concentrations of land cover affect temperature change.
"""

import numpy as np
import pandas as pd
import rasterio
import glob
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import warnings
warnings.filterwarnings('ignore')

# Dynamic World class names
DW_CLASSES = {
    0: 'Water',
    1: 'Trees',
    2: 'Grass',
    3: 'Flooded vegetation',
    4: 'Crops',
    5: 'Shrub & Scrub',
    6: 'Built',
    7: 'Bare',
    8: 'Snow & Ice'
}

def load_temperature_data():
    """Load and process temperature data"""
    print("Loading temperature data...")
    
    # Load historical and future files
    historical_files = glob.glob('data/maca/MACA_Seasonal-historical-GFDL-ESM2M-tasmax/*2001_2003*.tif')
    future_files = glob.glob('data/maca/MACA_Seasonal-rcp85-GFDL-ESM2M-tasmax/*2048_2050*.tif')
    
    print(f"Found {len(historical_files)} historical files")
    print(f"Found {len(future_files)} future files")
    
    # Process temperature data
    historical_temps = []
    for f in historical_files:
        with rasterio.open(f) as src:
            temp = src.read(1)
            if temp.mean() > 200:  # Convert from Kelvin
                temp = temp - 273.15
            historical_temps.append(temp)
            # Save metadata from first file
            if len(historical_temps) == 1:
                temp_transform = src.transform
                temp_crs = src.crs
    
    future_temps = []
    for f in future_files:
        with rasterio.open(f) as src:
            temp = src.read(1)
            if temp.mean() > 200:
                temp = temp - 273.15
            future_temps.append(temp)
    
    historical_avg = np.mean(historical_temps, axis=0)
    future_avg = np.mean(future_temps, axis=0)
    temp_change = future_avg - historical_avg
    
    print(f"Temperature change: {temp_change.mean():.2f} ± {temp_change.std():.2f}°C")
    print(f"Temperature grid shape: {temp_change.shape}")
    
    return temp_change, temp_transform

def load_landcover_data():
    """Load land cover data"""
    print("Loading land cover data...")
    
    with rasterio.open('data/DW_BlackHills_mode.tif') as src:
        landcover = src.read(1)
        lc_transform = src.transform
        lc_crs = src.crs
    
    print(f"Land cover shape: {landcover.shape}")
    return landcover, lc_transform

def calculate_landcover_percentages_in_temp_pixels(landcover, lc_transform, 
                                                  temp_shape, temp_transform):
    """
    Calculate land cover percentages within each temperature pixel
    
    Returns:
    - percentages: Array of shape (temp_height, temp_width, 9) with percentages for each class
    """
    print("Calculating land cover percentages within temperature pixels...")
    
    temp_height, temp_width = temp_shape
    percentages = np.zeros((temp_height, temp_width, 9))
    
    # Calculate pixel size ratios
    temp_pixel_size_x = abs(temp_transform[0])  # Temperature pixel width
    temp_pixel_size_y = abs(temp_transform[4])  # Temperature pixel height
    lc_pixel_size_x = abs(lc_transform[0])      # Land cover pixel width  
    lc_pixel_size_y = abs(lc_transform[4])      # Land cover pixel height
    
    # How many land cover pixels per temperature pixel
    lc_per_temp_x = int(round(temp_pixel_size_x / lc_pixel_size_x))
    lc_per_temp_y = int(round(temp_pixel_size_y / lc_pixel_size_y))
    
    print(f"  Land cover pixels per temperature pixel: {lc_per_temp_x} x {lc_per_temp_y}")
    print(f"  Processing {temp_height * temp_width} temperature pixels...")
    
    # For each temperature pixel, calculate land cover percentages
    for temp_row in range(temp_height):
        if temp_row % 5 == 0:  # Progress indicator
            print(f"    Processing row {temp_row}/{temp_height}")
            
        for temp_col in range(temp_width):
            # Calculate corresponding land cover pixel ranges
            lc_row_start = temp_row * lc_per_temp_y
            lc_row_end = min(lc_row_start + lc_per_temp_y, landcover.shape[0])
            lc_col_start = temp_col * lc_per_temp_x
            lc_col_end = min(lc_col_start + lc_per_temp_x, landcover.shape[1])
            
            # Extract land cover pixels within this temperature pixel
            lc_subset = landcover[lc_row_start:lc_row_end, lc_col_start:lc_col_end]
            
            # Calculate percentages for each class (0-8)
            valid_pixels = lc_subset[lc_subset != -9999]  # Exclude no-data
            
            if len(valid_pixels) > 0:
                for class_id in range(9):
                    count = np.sum(valid_pixels == class_id)
                    percentages[temp_row, temp_col, class_id] = (count / len(valid_pixels)) * 100
    
    print("  Land cover percentage calculation complete!")
    return percentages

def create_scatter_plots(temp_change, landcover_percentages):
    """Create scatter plots for each land cover type"""
    print("Creating scatter plots for each land cover type...")
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8-whitegrid')
    sns.set_palette("husl")
    
    # Create a figure with subplots for each land cover type
    fig, axes = plt.subplots(3, 3, figsize=(8, 8))
    axes = axes.flatten()
    
    # Store correlation results
    correlation_results = []
    
    # Get unique land cover classes present in the data
    present_classes = []
    for class_id in range(9):
        if landcover_percentages[:, :, class_id].max() > 0:
            present_classes.append(class_id)
    
    for i, class_id in enumerate(present_classes):
        if i >= 9:  # Only process first 9 classes
            break
            
        class_name = DW_CLASSES[class_id]
        
        # Extract data for this land cover class
        percentages_flat = landcover_percentages[:, :, class_id].flatten()
        temp_change_flat = temp_change.flatten()
        
        # Remove pixels with no data
        valid_mask = ~np.isnan(temp_change_flat)
        percentages_valid = percentages_flat[valid_mask]
        temp_change_valid = temp_change_flat[valid_mask]
        
        # Only include pixels where this land cover is present (>0%)
        present_mask = percentages_valid > 0
        percentages_present = percentages_valid[present_mask]
        temp_change_present = temp_change_valid[present_mask]
        
        if len(percentages_present) > 5:  # Need minimum points for analysis
            # Calculate correlation
            correlation, p_value = stats.pearsonr(percentages_present, temp_change_present)
            
            # Fit linear regression
            X = percentages_present.reshape(-1, 1)
            y = temp_change_present
            reg = LinearRegression().fit(X, y)
            r2 = r2_score(y, reg.predict(X))
            slope = reg.coef_[0]
            intercept = reg.intercept_
            
            # Store results
            correlation_results.append({
                'land_cover': class_name,
                'correlation': correlation,
                'p_value': p_value,
                'r_squared': r2,
                'slope': slope,
                'intercept': intercept,
                'n_pixels': len(percentages_present),
                'mean_percentage': percentages_present.mean(),
                'max_percentage': percentages_present.max()
            })
            
            # Create scatter plot
            ax = axes[i]
            scatter = ax.scatter(percentages_present, temp_change_present, 
                               alpha=0.6, s=30, edgecolors='black', linewidth=0.5)
            
            # Add trend line
            x_trend = np.linspace(0, percentages_present.max(), 100)
            y_trend = reg.predict(x_trend.reshape(-1, 1))
            ax.plot(x_trend, y_trend, 'red', linewidth=2, alpha=0.8)
            
            # Formatting
            ax.set_xlabel(f'{class_name} Percentage (%)')
            ax.set_ylabel('Temperature Change (°C)')
            ax.set_title(f'{class_name}\nR² = {r2:.3f}, p = {p_value:.3f}\nSlope = {slope:.4f}°C/%')
            ax.grid(True, alpha=0.3)
            
            # Color points by density if many points
            if len(percentages_present) > 50:
                # Add density information to scatter plot
                ax.hexbin(percentages_present, temp_change_present, gridsize=20, alpha=0.6, cmap='Blues')
        else:
            # Not enough data
            axes[i].text(0.5, 0.5, f'{class_name}\nInsufficient Data\n({len(percentages_present)} pixels)', 
                        ha='center', va='center', transform=axes[i].transAxes)
            axes[i].set_xlabel(f'{class_name} Percentage (%)')
            axes[i].set_ylabel('Temperature Change (°C)')
    
    # Hide unused subplots
    for j in range(len(present_classes), 9):
        axes[j].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('landcover_percentage_scatter_plots.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return pd.DataFrame(correlation_results)

def create_summary_analysis(correlation_results):
    """Create summary analysis and additional visualizations"""
    print("Creating summary analysis...")
    
    # Sort by correlation strength
    correlation_results_sorted = correlation_results.reindex(
        correlation_results['r_squared'].abs().sort_values(ascending=False).index
    )
    
    # Create summary visualizations
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(8, 8))
    
    # 1. R-squared values
    bars1 = ax1.bar(correlation_results_sorted['land_cover'], 
                   correlation_results_sorted['r_squared'])
    ax1.set_xlabel('Land Cover Type')
    ax1.set_ylabel('R² (Explained Variance)')
    ax1.set_title('Predictive Power of Land Cover Percentage')
    ax1.tick_params(axis='x', rotation=45)
    
    # Color bars by R-squared strength
    for bar, r2 in zip(bars1, correlation_results_sorted['r_squared']):
        if r2 > 0.1:
            bar.set_color('darkgreen')
        elif r2 > 0.05:
            bar.set_color('orange')
        else:
            bar.set_color('lightcoral')
    
    # 2. Correlation coefficients
    bars2 = ax2.bar(correlation_results_sorted['land_cover'], 
                   correlation_results_sorted['correlation'])
    ax2.set_xlabel('Land Cover Type')
    ax2.set_ylabel('Correlation Coefficient')
    ax2.set_title('Correlation: Land Cover % vs Temperature Change')
    ax2.tick_params(axis='x', rotation=45)
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # Color bars by correlation direction
    for bar, corr in zip(bars2, correlation_results_sorted['correlation']):
        if corr > 0:
            bar.set_color('red')  # Positive correlation (more land cover = more warming)
        else:
            bar.set_color('blue')  # Negative correlation (more land cover = less warming)
    
    # 3. Slope values (effect size)
    bars3 = ax3.bar(correlation_results_sorted['land_cover'], 
                   correlation_results_sorted['slope'])
    ax3.set_xlabel('Land Cover Type')
    ax3.set_ylabel('Slope (°C per % land cover)')
    ax3.set_title('Effect Size: Temperature Change per % Land Cover')
    ax3.tick_params(axis='x', rotation=45)
    ax3.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    
    # 4. Statistical significance
    log_p_values = -np.log10(correlation_results_sorted['p_value'])
    bars4 = ax4.bar(correlation_results_sorted['land_cover'], log_p_values)
    ax4.set_xlabel('Land Cover Type')
    ax4.set_ylabel('-log10(p-value)')
    ax4.set_title('Statistical Significance of Correlations')
    ax4.tick_params(axis='x', rotation=45)
    ax4.axhline(y=1.301, color='red', linestyle='--', alpha=0.7, label='p=0.05')
    ax4.legend()
    
    # Color bars by significance
    for bar, p_val in zip(bars4, correlation_results_sorted['p_value']):
        if p_val < 0.01:
            bar.set_color('darkgreen')
        elif p_val < 0.05:
            bar.set_color('orange')
        else:
            bar.set_color('lightcoral')
    
    plt.tight_layout()
    plt.savefig('landcover_correlation_summary.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    """Main analysis function"""
    print("Land Cover Percentage vs Temperature Change Analysis")
    print("=" * 60)
    
    # Load data
    temp_change, temp_transform = load_temperature_data()
    landcover, lc_transform = load_landcover_data()
    
    # Calculate land cover percentages within each temperature pixel
    landcover_percentages = calculate_landcover_percentages_in_temp_pixels(
        landcover, lc_transform, temp_change.shape, temp_transform
    )
    
    # Create scatter plots for each land cover type
    correlation_results = create_scatter_plots(temp_change, landcover_percentages)
    
    # Display results
    print("\nCorrelation Results:")
    print("=" * 60)
    print(correlation_results.round(4))
    
    # Create summary analysis
    create_summary_analysis(correlation_results)
    
    # Print key findings
    print("\n" + "=" * 60)
    print("KEY FINDINGS:")
    print("=" * 60)
    
    # Sort by R-squared to find strongest relationships
    strongest = correlation_results.loc[correlation_results['r_squared'].idxmax()]
    print(f"\n🏆 Strongest relationship: {strongest['land_cover']}")
    print(f"   R² = {strongest['r_squared']:.3f} (explains {strongest['r_squared']*100:.1f}% of variance)")
    print(f"   Correlation = {strongest['correlation']:.3f}")
    print(f"   Effect: {strongest['slope']:.4f}°C per 1% increase in {strongest['land_cover']}")
    
    # Find cooling vs warming land covers
    cooling_covers = correlation_results[correlation_results['slope'] < 0]
    warming_covers = correlation_results[correlation_results['slope'] > 0]
    
    if not cooling_covers.empty:
        print(f"\n❄️  COOLING land covers (negative slope):")
        for _, row in cooling_covers.iterrows():
            print(f"   • {row['land_cover']}: {row['slope']:.4f}°C per 1%")
    
    if not warming_covers.empty:
        print(f"\n🔥 WARMING land covers (positive slope):")
        for _, row in warming_covers.iterrows():
            print(f"   • {row['land_cover']}: {row['slope']:.4f}°C per 1%")
    
    # Save results
    correlation_results.to_csv('landcover_percentage_correlations.csv', index=False)
    
    # Save the full dataset for further analysis
    output_data = []
    for row in range(temp_change.shape[0]):
        for col in range(temp_change.shape[1]):
            if not np.isnan(temp_change[row, col]):
                pixel_data = {
                    'row': row,
                    'col': col,
                    'temp_change': temp_change[row, col]
                }
                for class_id in range(9):
                    pixel_data[f'pct_{DW_CLASSES[class_id].lower().replace(" ", "_")}'] = landcover_percentages[row, col, class_id]
                output_data.append(pixel_data)
    
    pd.DataFrame(output_data).to_csv('pixel_landcover_temperature_data.csv', index=False)
    
    print(f"\n💾 Results saved to:")
    print(f"   - landcover_percentage_correlations.csv")
    print(f"   - pixel_landcover_temperature_data.csv")

if __name__ == "__main__":
    main()