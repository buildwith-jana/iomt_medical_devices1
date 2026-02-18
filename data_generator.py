"""
Medical Device Data Generator with Anomaly Injection
Generates realistic medical device data with normal behavior, faults, and attacks
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class MedicalDeviceDataGenerator:
    def __init__(self, device_type='heart_monitor', seed=42):
        self.device_type = device_type
        np.random.seed(seed)
        random.seed(seed)
        
    def generate_normal_data(self, num_samples=1000, device_id='DEV001'):
        """Generate normal medical device data"""
        timestamps = [datetime.now() + timedelta(seconds=i*5) for i in range(num_samples)]
        
        if self.device_type == 'heart_monitor':
            # Normal heart rate: 60-100 bpm with some variation
            base_hr = 75
            heart_rate = base_hr + np.random.normal(0, 5, num_samples)
            heart_rate = np.clip(heart_rate, 55, 105)
            
            # Add circadian rhythm (lower at night)
            hours = np.array([ts.hour for ts in timestamps])
            circadian = -10 * np.cos(2 * np.pi * hours / 24)
            heart_rate += circadian
            
            # Blood oxygen: 95-100%
            spo2 = 97 + np.random.normal(0, 1, num_samples)
            spo2 = np.clip(spo2, 94, 100)
            
            # Temperature: 36.5-37.5°C
            temperature = 37.0 + np.random.normal(0, 0.2, num_samples)
            
        elif self.device_type == 'insulin_pump':
            # Insulin delivery rate (units/hour)
            heart_rate = np.random.uniform(0.5, 2.0, num_samples)
            spo2 = 98 + np.random.normal(0, 0.5, num_samples)  # placeholder
            temperature = 37.0 + np.random.normal(0, 0.1, num_samples)
            
        df = pd.DataFrame({
            'timestamp': timestamps,
            'device_id': device_id,
            'heart_rate': heart_rate,
            'spo2': spo2,
            'temperature': temperature,
            'label': 'normal',
            'anomaly_type': 'none'
        })
        
        return df
    
    def inject_hardware_faults(self, df, fault_percentage=0.1):
        """Inject hardware fault patterns"""
        num_faults = int(len(df) * fault_percentage)
        fault_indices = random.sample(range(len(df) - 20), num_faults)  # Leave buffer at end
        
        df_faults = df.copy()
        
        for idx in fault_indices:
            fault_type = random.choice(['sensor_drift', 'missing_data', 'battery_low', 'disconnection'])
            
            if fault_type == 'sensor_drift':
                # Gradual drift in readings
                length = min(20, len(df_faults) - idx)
                current_vals = df_faults.loc[idx:idx+length-1, 'heart_rate'].values
                actual_length = len(current_vals)
                if actual_length > 1:
                    drift = np.linspace(0, 15, actual_length)
                    df_faults.loc[idx:idx+actual_length-1, 'heart_rate'] = current_vals + drift
                    df_faults.loc[idx:idx+actual_length-1, 'label'] = 'fault'
                    df_faults.loc[idx:idx+actual_length-1, 'anomaly_type'] = 'sensor_drift'
                
            elif fault_type == 'missing_data':
                # Sporadic missing readings (represented as zeros)
                length = min(5, len(df_faults) - idx)
                df_faults.loc[idx:idx+length-1, 'heart_rate'] = 0
                df_faults.loc[idx:idx+length-1, 'spo2'] = 0
                df_faults.loc[idx:idx+length-1, 'label'] = 'fault'
                df_faults.loc[idx:idx+length-1, 'anomaly_type'] = 'missing_data'
                
            elif fault_type == 'battery_low':
                # Erratic readings when battery is low
                length = min(10, len(df_faults) - idx)
                current_vals = df_faults.loc[idx:idx+length-1, 'heart_rate'].values
                actual_length = len(current_vals)  # Actual number of values retrieved
                noise = np.random.uniform(-10, 10, actual_length)
                df_faults.loc[idx:idx+actual_length-1, 'heart_rate'] = current_vals + noise
                df_faults.loc[idx:idx+actual_length-1, 'label'] = 'fault'
                df_faults.loc[idx:idx+actual_length-1, 'anomaly_type'] = 'battery_low'
                
            elif fault_type == 'disconnection':
                # Sudden flatline
                length = min(8, len(df_faults) - idx)
                flatline_hr = df_faults.loc[idx, 'heart_rate']
                flatline_spo2 = df_faults.loc[idx, 'spo2']
                df_faults.loc[idx:idx+length-1, 'heart_rate'] = flatline_hr
                df_faults.loc[idx:idx+length-1, 'spo2'] = flatline_spo2
                df_faults.loc[idx:idx+length-1, 'label'] = 'fault'
                df_faults.loc[idx:idx+length-1, 'anomaly_type'] = 'disconnection'
        
        return df_faults
    
    def inject_cyber_attacks(self, df, attack_percentage=0.1):
        """Inject cyber attack patterns"""
        num_attacks = int(len(df) * attack_percentage)
        attack_indices = random.sample(range(50, len(df) - 20), num_attacks)  # Leave buffer
        
        df_attacks = df.copy()
        
        for idx in attack_indices:
            attack_type = random.choice(['data_injection', 'replay_attack', 'timing_manipulation', 'spoofing'])
            
            if attack_type == 'data_injection':
                # Injected false high/low values
                injected_value = random.choice([50, 150])
                length = min(3, len(df_attacks) - idx)
                df_attacks.loc[idx:idx+length-1, 'heart_rate'] = injected_value
                df_attacks.loc[idx:idx+length-1, 'label'] = 'attack'
                df_attacks.loc[idx:idx+length-1, 'anomaly_type'] = 'data_injection'
                
            elif attack_type == 'replay_attack':
                # Repeated data pattern (attacker replaying old data)
                replay_start = idx - 20
                length = min(9, len(df_attacks) - idx)
                replay_data = df_attacks.loc[replay_start:replay_start+length-1, 'heart_rate'].values
                if len(replay_data) == length:
                    df_attacks.loc[idx:idx+length-1, 'heart_rate'] = replay_data
                    df_attacks.loc[idx:idx+length-1, 'label'] = 'attack'
                    df_attacks.loc[idx:idx+length-1, 'anomaly_type'] = 'replay_attack'
                    
            elif attack_type == 'timing_manipulation':
                # Irregular timestamps (attacker manipulating time)
                length = min(5, len(df_attacks) - idx)
                time_offset = timedelta(seconds=random.randint(100, 500))
                for i in range(idx, idx + length):
                    df_attacks.loc[i, 'timestamp'] = df_attacks.loc[i, 'timestamp'] + time_offset
                df_attacks.loc[idx:idx+length-1, 'label'] = 'attack'
                df_attacks.loc[idx:idx+length-1, 'anomaly_type'] = 'timing_manipulation'
                
            elif attack_type == 'spoofing':
                # Subtle data manipulation (harder to detect)
                length = min(14, len(df_attacks) - idx)
                current_vals = df_attacks.loc[idx:idx+length-1, 'heart_rate'].values
                actual_length = len(current_vals)
                manipulation = np.random.uniform(5, 12, actual_length)
                df_attacks.loc[idx:idx+actual_length-1, 'heart_rate'] = current_vals + manipulation
                df_attacks.loc[idx:idx+actual_length-1, 'spo2'] -= 2
                df_attacks.loc[idx:idx+actual_length-1, 'label'] = 'attack'
                df_attacks.loc[idx:idx+actual_length-1, 'anomaly_type'] = 'spoofing'
        
        return df_attacks
    
    def generate_complete_dataset(self, num_samples=2000, fault_pct=0.15, attack_pct=0.15):
        """Generate complete dataset with normal, faults, and attacks"""
        # Generate normal data
        df_normal = self.generate_normal_data(num_samples=num_samples)
        
        # Split into three parts
        split1 = int(num_samples * 0.4)
        split2 = int(num_samples * 0.7)
        
        df_part1 = df_normal.iloc[:split1].copy().reset_index(drop=True)  # Pure normal
        df_part2 = df_normal.iloc[split1:split2].copy().reset_index(drop=True)  # Will have faults
        df_part3 = df_normal.iloc[split2:].copy().reset_index(drop=True)  # Will have attacks
        
        # Inject faults and attacks
        df_part2 = self.inject_hardware_faults(df_part2, fault_percentage=fault_pct)
        df_part3 = self.inject_cyber_attacks(df_part3, attack_percentage=attack_pct)
        
        # Combine all
        df_complete = pd.concat([df_part1, df_part2, df_part3], ignore_index=True)
        
        # Shuffle
        df_complete = df_complete.sample(frac=1, random_state=42).reset_index(drop=True)
        
        return df_complete


def add_time_features(df):
    """Add time-based features for ML"""
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    # Time difference between consecutive readings
    df['time_diff'] = df['timestamp'].diff().dt.total_seconds().fillna(5.0)
    
    # Rolling statistics
    df['hr_rolling_mean'] = df['heart_rate'].rolling(window=5, min_periods=1).mean()
    df['hr_rolling_std'] = df['heart_rate'].rolling(window=5, min_periods=1).std().fillna(0)
    df['hr_rate_of_change'] = df['heart_rate'].diff().fillna(0)
    
    return df


if __name__ == "__main__":
    # Test the generator
    generator = MedicalDeviceDataGenerator(device_type='heart_monitor')
    df = generator.generate_complete_dataset(num_samples=2000)
    df = add_time_features(df)
    
    print("Dataset generated successfully!")
    print(f"Total samples: {len(df)}")
    print(f"\nLabel distribution:")
    print(df['label'].value_counts())
    print(f"\nAnomaly type distribution:")
    print(df['anomaly_type'].value_counts())
    print(f"\nSample data:")
    print(df.head(10))
