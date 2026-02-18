"""
ML Models for Medical Device Anomaly Detection
Multi-class classification: Normal, Fault, Attack
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import json


class AnomalyDetectionModel:
    def __init__(self, model_type='multiclass'):
        self.model_type = model_type
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.model = None
        self.feature_columns = None
        
    def prepare_features(self, df):
        """Prepare features for ML model"""
        feature_cols = [
            'heart_rate', 'spo2', 'temperature',
            'hour', 'minute', 'day_of_week', 'time_diff',
            'hr_rolling_mean', 'hr_rolling_std', 'hr_rate_of_change'
        ]
        
        self.feature_columns = feature_cols
        X = df[feature_cols].copy()
        
        # Handle any remaining NaN values
        X = X.fillna(method='ffill').fillna(method='bfill').fillna(0)
        
        return X
    
    def train_multiclass_model(self, df):
        """Train multi-class classifier (Normal, Fault, Attack)"""
        print("Training multi-class classifier...")
        
        X = self.prepare_features(df)
        y = df['label'].values
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.3, random_state=42, stratify=y_encoded
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest Classifier
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        
        print("\n" + "="*60)
        print("MODEL EVALUATION RESULTS")
        print("="*60)
        
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nOverall Accuracy: {accuracy:.4f}")
        
        print("\nClassification Report:")
        print(classification_report(
            y_test, y_pred, 
            target_names=self.label_encoder.classes_
        ))
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 5 Most Important Features:")
        print(feature_importance.head())
        
        return {
            'accuracy': accuracy,
            'classification_report': classification_report(y_test, y_pred, target_names=self.label_encoder.classes_, output_dict=True),
            'feature_importance': feature_importance.to_dict('records')
        }
    
    def train_isolation_forest(self, df):
        """Train Isolation Forest for anomaly detection (binary)"""
        print("Training Isolation Forest...")
        
        X = self.prepare_features(df)
        
        # Use only normal data for training
        normal_mask = df['label'] == 'normal'
        X_normal = X[normal_mask]
        
        # Scale features
        X_normal_scaled = self.scaler.fit_transform(X_normal)
        
        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=0.2,
            random_state=42,
            n_estimators=100
        )
        
        self.model.fit(X_normal_scaled)
        
        # Evaluate on full dataset
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        
        # -1 for anomaly, 1 for normal
        anomaly_scores = self.model.score_samples(X_scaled)
        
        # Map predictions: 1 (normal) -> 0, -1 (anomaly) -> 1
        predictions_binary = (predictions == -1).astype(int)
        
        # Create ground truth binary labels
        y_true_binary = (df['label'] != 'normal').astype(int)
        
        accuracy = accuracy_score(y_true_binary, predictions_binary)
        print(f"\nAnomaly Detection Accuracy: {accuracy:.4f}")
        
        return {
            'accuracy': accuracy,
            'anomaly_scores': anomaly_scores
        }
    
    def predict(self, df):
        """Make predictions on new data"""
        X = self.prepare_features(df)
        X_scaled = self.scaler.transform(X)
        
        if self.model_type == 'multiclass':
            predictions = self.model.predict(X_scaled)
            probabilities = self.model.predict_proba(X_scaled)
            
            # Decode labels
            predicted_labels = self.label_encoder.inverse_transform(predictions)
            
            return predicted_labels, probabilities
        else:
            predictions = self.model.predict(X_scaled)
            anomaly_scores = self.model.score_samples(X_scaled)
            return predictions, anomaly_scores
    
    def get_feature_importance(self):
        """Get feature importance for explainability"""
        if hasattr(self.model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            return importance_df
        return None
    
    def save_model(self, filepath='model_artifacts'):
        """Save model and preprocessing objects"""
        import os
        os.makedirs(filepath, exist_ok=True)
        
        joblib.dump(self.model, f'{filepath}/model.pkl')
        joblib.dump(self.scaler, f'{filepath}/scaler.pkl')
        joblib.dump(self.label_encoder, f'{filepath}/label_encoder.pkl')
        
        # Save metadata
        metadata = {
            'model_type': self.model_type,
            'feature_columns': self.feature_columns,
            'classes': self.label_encoder.classes_.tolist() if hasattr(self.label_encoder, 'classes_') else None
        }
        
        with open(f'{filepath}/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Model saved to {filepath}/")
    
    def load_model(self, filepath='model_artifacts'):
        """Load saved model"""
        self.model = joblib.load(f'{filepath}/model.pkl')
        self.scaler = joblib.load(f'{filepath}/scaler.pkl')
        self.label_encoder = joblib.load(f'{filepath}/label_encoder.pkl')
        
        with open(f'{filepath}/metadata.json', 'r') as f:
            metadata = json.load(f)
        
        self.model_type = metadata['model_type']
        self.feature_columns = metadata['feature_columns']
        
        print(f"Model loaded from {filepath}/")


class ExplainabilityModule:
    """Generate explanations for predictions"""
    
    @staticmethod
    def explain_prediction(df_row, prediction, probability, feature_importance):
        """Generate human-readable explanation"""
        explanation = {
            'prediction': prediction,
            'confidence': f"{max(probability)*100:.1f}%",
            'reasons': []
        }
        
        # Analyze key features
        if df_row['hr_rate_of_change'] > 10:
            explanation['reasons'].append("Sudden change in heart rate detected")
        
        if df_row['hr_rolling_std'] > 8:
            explanation['reasons'].append("High variability in readings")
        
        if df_row['time_diff'] > 10:
            explanation['reasons'].append("Irregular timing between readings")
        
        if df_row['heart_rate'] < 50 or df_row['heart_rate'] > 120:
            explanation['reasons'].append("Heart rate outside normal range")
        
        if prediction == 'attack':
            explanation['reasons'].append("Pattern matches known attack signatures")
            explanation['recommendation'] = "Alert security team - possible cyber intrusion"
        elif prediction == 'fault':
            explanation['reasons'].append("Pattern matches hardware malfunction")
            explanation['recommendation'] = "Alert maintenance team - device may need servicing"
        else:
            explanation['recommendation'] = "Continue normal monitoring"
        
        return explanation


if __name__ == "__main__":
    # Test the model
    from data_generator import MedicalDeviceDataGenerator, add_time_features
    
    print("Generating test data...")
    generator = MedicalDeviceDataGenerator()
    df = generator.generate_complete_dataset(num_samples=2000)
    df = add_time_features(df)
    
    print("\nTraining model...")
    model = AnomalyDetectionModel(model_type='multiclass')
    results = model.train_multiclass_model(df)
    
    print("\nSaving model...")
    model.save_model()
    
    print("\nModel training complete!")
