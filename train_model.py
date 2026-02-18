"""
Main Training Script
Trains the ML model and generates evaluation reports
"""

import pandas as pd
import numpy as np
from data_generator import MedicalDeviceDataGenerator, add_time_features
from ml_models import AnomalyDetectionModel
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import os

def main():
    print("="*70)
    print("MEDICAL DEVICE SECURITY - ML MODEL TRAINING")
    print("="*70)
    
    # Step 1: Generate Data
    print("\n[1/4] Generating synthetic medical device data...")
    generator = MedicalDeviceDataGenerator(device_type='heart_monitor', seed=42)
    df = generator.generate_complete_dataset(
        num_samples=2000,
        fault_pct=0.15,
        attack_pct=0.15
    )
    
    print(f"✓ Generated {len(df)} samples")
    print(f"  - Normal: {(df['label'] == 'normal').sum()}")
    print(f"  - Faults: {(df['label'] == 'fault').sum()}")
    print(f"  - Attacks: {(df['label'] == 'attack').sum()}")
    
    # Step 2: Add Features
    print("\n[2/4] Engineering time-series features...")
    df = add_time_features(df)
    print(f"✓ Added {len(df.columns)} features")
    
    # Step 3: Train Model
    print("\n[3/4] Training Random Forest Classifier...")
    model = AnomalyDetectionModel(model_type='multiclass')
    results = model.train_multiclass_model(df)
    
    # Step 4: Save Model
    print("\n[4/4] Saving model artifacts...")
    model.save_model('model_artifacts')
    
    # Save sample data for dashboard
    df_sample = df.sample(n=500, random_state=42)
    df_sample.to_csv('sample_data.csv', index=False)
    print("✓ Saved sample data to sample_data.csv")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    
    # Feature importance
    importance_df = model.get_feature_importance()
    plt.figure(figsize=(10, 6))
    plt.barh(importance_df['feature'][:10], importance_df['importance'][:10])
    plt.xlabel('Importance')
    plt.title('Top 10 Most Important Features')
    plt.tight_layout()
    plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
    print("✓ Saved feature_importance.png")
    
    # Anomaly distribution
    plt.figure(figsize=(8, 6))
    df['label'].value_counts().plot(kind='bar', color=['green', 'orange', 'red'])
    plt.xlabel('Category')
    plt.ylabel('Count')
    plt.title('Data Distribution by Category')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('data_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Saved data_distribution.png")
    
    print("\n" + "="*70)
    print("TRAINING COMPLETE!")
    print("="*70)
    print(f"\n✓ Model Accuracy: {results['accuracy']*100:.2f}%")
    print(f"✓ Model artifacts saved to: model_artifacts/")
    print(f"✓ Visualizations saved as PNG files")
    print(f"\nTo run the dashboard:")
    print(f"  streamlit run dashboard.py")
    print("="*70)


if __name__ == "__main__":
    main()
