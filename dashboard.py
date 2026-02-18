"""
Medical Device Security Monitoring Dashboard
Real-time anomaly detection and alert system
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_generator import MedicalDeviceDataGenerator, add_time_features
from ml_models import AnomalyDetectionModel, ExplainabilityModule

# Page config
st.set_page_config(
    page_title="Medical Device Security Monitor",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .alert-box {
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .alert-critical {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .alert-warning {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
    }
    .alert-normal {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
    }
    .metric-card {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_model():
    """Load the trained ML model"""
    model = AnomalyDetectionModel(model_type='multiclass')
    try:
        model.load_model('model_artifacts')
        return model
    except:
        st.warning("Model not found. Training new model...")
        # Generate data and train
        generator = MedicalDeviceDataGenerator()
        df = generator.generate_complete_dataset(num_samples=2000)
        df = add_time_features(df)
        model.train_multiclass_model(df)
        model.save_model()
        return model


@st.cache_data
def generate_demo_data(num_samples=500):
    """Generate demo data for visualization"""
    generator = MedicalDeviceDataGenerator(device_type='heart_monitor')
    df = generator.generate_complete_dataset(num_samples=num_samples)
    df = add_time_features(df)
    return df


def create_time_series_plot(df, highlight_anomalies=True):
    """Create interactive time series plot"""
    fig = go.Figure()
    
    if highlight_anomalies:
        # Plot by category
        for label in ['normal', 'fault', 'attack']:
            mask = df['label'] == label
            color = {'normal': 'green', 'fault': 'orange', 'attack': 'red'}[label]
            fig.add_trace(go.Scatter(
                x=df[mask]['timestamp'],
                y=df[mask]['heart_rate'],
                mode='lines+markers',
                name=label.capitalize(),
                marker=dict(size=4, color=color),
                line=dict(width=1)
            ))
    else:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['heart_rate'],
            mode='lines',
            name='Heart Rate',
            line=dict(color='blue', width=2)
        ))
    
    fig.update_layout(
        title='Medical Device Time Series Data',
        xaxis_title='Time',
        yaxis_title='Heart Rate (BPM)',
        height=400,
        hovermode='x unified'
    )
    
    return fig


def create_anomaly_distribution_plot(df):
    """Create pie chart of anomaly distribution"""
    counts = df['label'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=counts.index,
        values=counts.values,
        hole=0.4,
        marker=dict(colors=['#4caf50', '#ff9800', '#f44336'])
    )])
    
    fig.update_layout(
        title='Detection Results Distribution',
        height=300
    )
    
    return fig


def create_feature_importance_plot(model):
    """Create feature importance bar chart"""
    importance_df = model.get_feature_importance()
    
    if importance_df is not None:
        fig = px.bar(
            importance_df.head(10),
            x='importance',
            y='feature',
            orientation='h',
            title='Top 10 Most Important Features'
        )
        fig.update_layout(height=400)
        return fig
    return None


def display_alert(prediction, confidence, reasons, timestamp):
    """Display alert with styling"""
    alert_class = {
        'normal': 'alert-normal',
        'fault': 'alert-warning',
        'attack': 'alert-critical'
    }[prediction]
    
    icon = {
        'normal': '✅',
        'fault': '⚠️',
        'attack': '🚨'
    }[prediction]
    
    st.markdown(f"""
        <div class="alert-box {alert_class}">
            <h3>{icon} {prediction.upper()} DETECTED</h3>
            <p><strong>Confidence:</strong> {confidence}</p>
            <p><strong>Time:</strong> {timestamp}</p>
            <p><strong>Reasons:</strong></p>
            <ul>
                {''.join([f'<li>{reason}</li>' for reason in reasons])}
            </ul>
        </div>
    """, unsafe_allow_html=True)


def main():
    st.title("🏥 Medical Device Security Monitoring System")
    st.markdown("### ML-Based Intrusion Detection for Healthcare IoT")
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    mode = st.sidebar.radio(
        "Select Mode",
        ["Real-time Monitoring", "Historical Analysis", "Model Performance"]
    )
    
    device_id = st.sidebar.selectbox(
        "Device ID",
        ["DEV001 - ICU Room 1", "DEV002 - ICU Room 2", "DEV003 - Emergency"]
    )
    
    # Load model
    model = load_model()
    
    if mode == "Real-time Monitoring":
        st.header("📊 Real-time Device Monitoring")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Devices Online", "3", delta="0")
        with col2:
            st.metric("Active Alerts", "0", delta="0")
        with col3:
            st.metric("Detection Accuracy", "94.2%", delta="1.2%")
        with col4:
            st.metric("Uptime", "99.8%", delta="0.1%")
        
        st.markdown("---")
        
        # Generate sample data stream
        if st.button("🔄 Start Monitoring Session", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            alert_placeholder = st.empty()
            chart_placeholder = st.empty()
            
            generator = MedicalDeviceDataGenerator()
            df = generator.generate_complete_dataset(num_samples=100)
            df = add_time_features(df)
            
            # Simulate real-time processing
            for i in range(0, len(df), 5):
                batch = df.iloc[i:i+5]
                
                # Make predictions
                predictions, probabilities = model.predict(batch)
                
                # Update display
                progress_bar.progress(min((i + 5) / len(df), 1.0))
                status_text.text(f"Processing readings {i+1} to {i+5}...")
                
                # Show chart
                chart_placeholder.plotly_chart(
                    create_time_series_plot(df.iloc[:i+5]),
                    use_container_width=True
                )
                
                # Check for anomalies
                for idx, (pred, prob) in enumerate(zip(predictions, probabilities)):
                    if pred != 'normal':
                        row = batch.iloc[idx]
                        explainer = ExplainabilityModule()
                        explanation = explainer.explain_prediction(
                            row, pred, prob, model.get_feature_importance()
                        )
                        
                        with alert_placeholder.container():
                            display_alert(
                                pred,
                                explanation['confidence'],
                                explanation['reasons'],
                                row['timestamp']
                            )
                
                time.sleep(0.5)
            
            st.success("✅ Monitoring session complete!")
    
    elif mode == "Historical Analysis":
        st.header("📈 Historical Data Analysis")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End Date", datetime.now())
        
        # Generate historical data
        df = generate_demo_data(num_samples=500)
        
        # Make predictions
        predictions, probabilities = model.predict(df)
        df['prediction'] = predictions
        df['confidence'] = [max(p) for p in probabilities]
        
        # Display summary
        st.subheader("Detection Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            normal_count = (df['prediction'] == 'normal').sum()
            st.metric("Normal Operations", f"{normal_count} ({normal_count/len(df)*100:.1f}%)")
        
        with col2:
            fault_count = (df['prediction'] == 'fault').sum()
            st.metric("Hardware Faults", f"{fault_count} ({fault_count/len(df)*100:.1f}%)")
        
        with col3:
            attack_count = (df['prediction'] == 'attack').sum()
            st.metric("Cyber Attacks", f"{attack_count} ({attack_count/len(df)*100:.1f}%)")
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(
                create_time_series_plot(df, highlight_anomalies=True),
                use_container_width=True
            )
        
        with col2:
            st.plotly_chart(
                create_anomaly_distribution_plot(df),
                use_container_width=True
            )
        
        # Detailed incidents table
        st.subheader("🔍 Detected Incidents")
        
        anomalies = df[df['prediction'] != 'normal'].copy()
        
        if len(anomalies) > 0:
            anomalies_display = anomalies[['timestamp', 'device_id', 'prediction', 'confidence', 'heart_rate', 'anomaly_type']].copy()
            anomalies_display['confidence'] = anomalies_display['confidence'].apply(lambda x: f"{x*100:.1f}%")
            
            st.dataframe(
                anomalies_display.sort_values('timestamp', ascending=False),
                use_container_width=True,
                height=300
            )
            
            # Export option
            csv = anomalies_display.to_csv(index=False)
            st.download_button(
                label="📥 Download Incident Report",
                data=csv,
                file_name=f"incident_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No anomalies detected in this period.")
    
    elif mode == "Model Performance":
        st.header("🎯 Model Performance Metrics")
        
        # Generate test data
        df = generate_demo_data(num_samples=500)
        
        # Evaluate model
        st.subheader("Classification Performance")
        
        predictions, probabilities = model.predict(df)
        
        from sklearn.metrics import classification_report, confusion_matrix
        
        # Classification report
        report = classification_report(df['label'], predictions, output_dict=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Overall Accuracy", f"{report['accuracy']*100:.2f}%")
        with col2:
            st.metric("Macro F1-Score", f"{report['macro avg']['f1-score']*100:.2f}%")
        with col3:
            st.metric("Weighted F1-Score", f"{report['weighted avg']['f1-score']*100:.2f}%")
        
        st.markdown("---")
        
        # Per-class metrics
        st.subheader("Per-Class Performance")
        
        metrics_data = []
        for label in ['normal', 'fault', 'attack']:
            if label in report:
                metrics_data.append({
                    'Class': label.capitalize(),
                    'Precision': f"{report[label]['precision']*100:.2f}%",
                    'Recall': f"{report[label]['recall']*100:.2f}%",
                    'F1-Score': f"{report[label]['f1-score']*100:.2f}%",
                    'Support': int(report[label]['support'])
                })
        
        st.table(pd.DataFrame(metrics_data))
        
        # Confusion Matrix
        st.subheader("Confusion Matrix")
        cm = confusion_matrix(df['label'], predictions, labels=['normal', 'fault', 'attack'])
        
        fig = px.imshow(
            cm,
            labels=dict(x="Predicted", y="Actual", color="Count"),
            x=['Normal', 'Fault', 'Attack'],
            y=['Normal', 'Fault', 'Attack'],
            text_auto=True,
            color_continuous_scale='Blues'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Feature Importance
        st.subheader("Feature Importance Analysis")
        importance_plot = create_feature_importance_plot(model)
        if importance_plot:
            st.plotly_chart(importance_plot, use_container_width=True)
        
        # Model info
        with st.expander("📋 Model Information"):
            st.write("**Model Type:** Random Forest Classifier")
            st.write("**Training Date:** ", datetime.now().strftime("%Y-%m-%d"))
            st.write("**Feature Count:** 10")
            st.write("**Classes:** Normal, Hardware Fault, Cyber Attack")


if __name__ == "__main__":
    main()
