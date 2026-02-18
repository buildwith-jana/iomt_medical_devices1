# Medical Device Security Monitor

A machine learning project that helps figure out if a medical device is broken or being hacked.

## The Problem

In hospitals, when a medical device starts acting weird, nobody knows if it's a hardware problem or a cyberattack. Security teams waste time investigating broken sensors. Maintenance teams might miss actual security threats. The alerts are useless because they don't tell you what's actually wrong.

I wanted to build something that could tell the difference.

## What It Does

This system uses machine learning to classify what's happening:

- **Normal** → Device is working fine
- **Hardware Fault** → Something's broken (sensor drift, loose connection, battery issue)
- **Cyber Attack** → Someone's tampering with the data

Instead of just saying "alert!", it tells you what kind of problem it is so the right team can handle it.

## How It Works

The model analyzes device readings (heart rate, oxygen levels, temperature) and looks for unusual patterns. I trained it to recognize:

- Normal device behavior (including natural variations)
- Hardware failures like sensor drift, missing data, battery issues
- Attack patterns like data injection, replay attacks, timing manipulation

Built with Python, scikit-learn for ML, and Streamlit for the dashboard.

## Results

Testing on synthetic data:
- Overall accuracy: ~87%
- Detects 96% of hardware faults
- Detects 87% of cyberattacks
- False positives: under 6%

_(Using synthetic data since real hospital data isn't available for academic projects)_

## Running the Project

```bash
git clone https://github.com/buildwith-jana/iomt_medical_devices1.git
cd iomt_medical_devices1

pip install -r requirements.txt
python train_model.py
streamlit run dashboard.py
```

Dashboard opens at `http://localhost:8501`

## Project Structure

```
├── data_generator.py      # Generates synthetic medical device data
├── ml_models.py           # ML model (Random Forest classifier)
├── train_model.py         # Training script
├── dashboard.py           # Streamlit web dashboard
├── requirements.txt       # Python dependencies
└── model_artifacts/       # Saved trained models
```

## The Dataset

I created synthetic medical device data for this project. It includes:
- ~2000 samples of device readings
- Normal patterns with realistic variations
- Simulated hardware faults (sensor drift, disconnections, battery issues)
- Simulated cyberattacks (data injection, replay attacks, spoofing)

No real patient data was used.

## Features

The model uses 10 features extracted from the time-series data:
- Raw vitals (heart rate, SpO2, temperature)
- Statistical patterns (rolling mean, standard deviation)
- Rate of change in readings
- Time-based features (hour of day, day of week)
- Timing intervals between readings

## Dashboard

Three main views:

**Real-time Monitoring**  
Watch the model detect anomalies as data streams in. Color-coded alerts show what it found.

**Historical Analysis**  
Review past incidents with charts and filtering. Export incident reports as CSV.

**Model Performance**  
Check accuracy metrics, confusion matrix, and feature importance.

## Why This Matters

Healthcare IoT security is a real problem. Hospitals need better ways to tell apart hardware failures and cyberattacks. This project shows how ML can help with that triage.

It's academic work, but the approach could be useful in real hospital security operations centers.

## Technical Details

- **Model:** Random Forest Classifier (200 trees)
- **Training:** 70/30 split, stratified sampling
- **Libraries:** scikit-learn, pandas, numpy, streamlit, plotly
- **Features:** 10 engineered time-series features
- **Classes:** 3 (normal, fault, attack)

## Limitations

- Synthetic data only (not validated on real devices)
- Single device type (heart monitor)
- No real-time streaming (simulated)
- Would need clinical validation for actual deployment

## Future Ideas

Some things that could make this better:
- Test on real medical device data (with proper approvals)
- Add support for multiple device types
- Use LSTM for better temporal pattern learning
- Connect to actual hospital monitoring systems
- Add explainability (SHAP values for each prediction)

## About

This is a personal project I built as part of my M.Tech coursework. Wanted to work on something at the intersection of cybersecurity and healthcare, since both areas interest me.

## Contact

**Srujana**  
Email: srujana.chikka0@gmail.com  
GitHub: [@buildwith-jana](https://github.com/buildwith-jana)

---

Built with Python • scikit-learn • Streamlit
