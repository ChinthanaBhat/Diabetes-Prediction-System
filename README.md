# Diabetes Prediction System

A machine learning web application that predicts whether a person is at risk of developing diabetes based on health-related features. The model is trained on a dataset containing information such as age, blood pressure, glucose level, BMI, and more.

## Features

- User registration and login with securely hashed passwords
- Upload a CSV dataset and preview its first rows
- Train a Random Forest model on the uploaded dataset from the browser
- Predict diabetes risk (positive / negative) from eight health measurements
- Data visualization: scatter plot of pregnancies vs glucose

## Tech Stack

- **Language:** Python
- **Web framework:** Flask, Flask-SQLAlchemy, Flask-Bcrypt
- **Database:** MySQL (via PyMySQL)
- **Machine learning:** scikit-learn (Random Forest), pandas, NumPy, joblib
- **Visualization:** matplotlib, seaborn
- **Frontend:** HTML, CSS (Jinja2 templates)

## Dataset

- **Source:** Kaggle
- **Records:** 768
- **Input features:** Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
- **Target:** Outcome (1 = diabetic, 0 = non-diabetic)

A copy of the dataset is included as `ML APP/diabetes.csv`.

## Methodology

1. Upload the dataset through the web interface
2. Split the data into 80% training and 20% test sets (`random_state=42`)
3. Train a Random Forest classifier with 100 trees
4. Save the trained model to `models/model.pkl`
5. Use the saved model to predict on new patient inputs

## Results

| Model | Test accuracy |
| --- | --- |
| Random Forest (100 trees) | ~72% |

Measured on the 20% held-out test split of the included dataset.

## Project Structure

```
├── ML APP/
│   ├── app.py              # Flask app: routes, training, prediction
│   ├── diabetes.csv        # Dataset
│   ├── models/model.pkl    # Trained model
│   ├── static/             # CSS and images
│   ├── templates/          # HTML pages
│   └── uploads/            # Uploaded datasets
├── requirements.txt
└── README.md
```

## Setup

**Prerequisites:** Python 3.9+ and MySQL installed and running.

1. Clone the repository
   ```bash
   git clone https://github.com/ChinthanaBhat/Diabetes-Prediction-System.git
   cd Diabetes-Prediction-System
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Create the MySQL database (the tables are created automatically on first run)
   ```sql
   CREATE DATABASE ml_app;
   ```
4. Open `ML APP/app.py` and set your MySQL username and password in `SQLALCHEMY_DATABASE_URI`
5. Run the app from inside the `ML APP` folder
   ```bash
   cd "ML APP"
   python app.py
   ```
6. Open `http://localhost:5000` in your browser, register an account, upload `diabetes.csv`, train the model, then predict

## Future Improvements

- Handle zero values in Glucose, BloodPressure, SkinThickness, Insulin and BMI, which represent missing data in this dataset
- Add feature scaling and compare more algorithms (Logistic Regression, SVM, KNN)
- Report precision, recall and F1-score alongside accuracy
- Move database credentials and the secret key into environment variables

## Disclaimer

This project is for educational purposes only and is not a substitute for professional medical advice or diagnosis.

## Author

Chinthana G Bhat
