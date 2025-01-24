from flask import * #flask is used to create web application development server=werkzeug

from flask_sqlalchemy import SQLAlchemy #object relational mapping tool
from flask_bcrypt import Bcrypt #provides secure password hashing

import os
from werkzeug.utils import secure_filename
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib

import matplotlib
matplotlib.use('Agg') #use non-GUI backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np


app=Flask(__name__)

app.secret_key = 'your_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:ROOT@localhost/ml_app' #connected to database mysql(pymysql=to specify the mysql database dialect)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #disables the overhead of tracking modifications to object

# Initialize SQLAlchemy
db = SQLAlchemy(app) #used to interact with connected database
# Initialize Bcrypt(used for securely hashing and verifying passwords)
bcrypt = Bcrypt(app)

# Define a database model - User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


    

@app.route('/')#python web framework. is a decorator used to associate a function with a specified url or a route
def index():
    #return "Flask is working!"
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST': #used to send data from client to server
        #Read the inputs from registration form
        username = request.form['username']#sahana
        email = request.form['email']
        password = request.form['password']
        #Password Encryption
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        # Create a new user
        new_user = User(username=username, email=email,
                        password=hashed_password)
        
        #Saving the user details to database table
        try:
            db.session.add(new_user)
            db.session.commit()#commit is to save the data
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Error: Username or email already exists.', 'danger')

    return render_template('register.html')
@app.route('/login',methods=['GET','POST'])#post is for privacy of the data
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']
        user=User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password,password):
            #successfull login
            session['user_id']=user.id
            session['username']=user.username#session is used to save current details
            flash('Login successful!','success')
            #return to dashboard
            return redirect(url_for('dashboard'))
        else:
            #Login failed
            flash('invalid email or password.please try again.','danger')
    return render_template('login.html')
@app.route('/dashboard')
def dashboard():
    if 'user_id'not in session:
        flash('please log in to access the dashboard.','warning')
        return redirect(url_for('login'))
    username=session['username']
    return render_template('dashboard.html',username=username)
@app.route('/logout',methods=['POST'])
def logout():
    #Remove user_id and username keys from session dictionary
    session.pop('user_id',None)
    session.pop('username',None)
    flash('You have been logged out.','info')
    return redirect (url_for('login'))
UPLOAD_FOLDER=os.path.join(os.path.abspath(os.getcwd()),'uploads')
ALLOWED_EXTENSIONS={'csv'}


app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER


#helper function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower()in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'post'])
def upload():
    global uploaded_data
    file_uploaded_data = False
    columns, data = [], []
    if request.method == 'POST':
        #check if the POST request has a file
        if 'file' not in request.files:
            flash('no files part','danger')
            return redirect(request.url)
        file = request.files['file']
        #check if a file is selected
        if file.filename == '':
                flash('no file selected.', 'warning')
                return redirect(request.url)
        if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
                file.save(file_path) #save the file
                file_uploaded = True
                flash('file uploaded succesfully!','success')
                #read the file and process it
                try:
                    uploaded_data = pd.read_csv(file_path)
                    columns = uploaded_data.columns.tolist()
                    data=uploaded_data.head(10).values.tolist()
                    return render_template('upload.html',file_uploaded=file_uploaded,columns=columns,data=data)
                except Exception as e:
                    flash(f'Error reading the file: {e}','danger')
                    return redirect(request.url)
        flash('Invalid file type.Please upload a CSV file.','danger')
        return redirect(request.url)
    #Render the upload page for GET requests
    return render_template('upload.html')


@app.route('/train',methods=['GET','POST'])
def train():
    global uploaded_data
    if uploaded_data is None:
        flash('No dataset uploaded.','warning')
        return redirect (url_for('upload'))
    try:
        #All columns except the last (features)
        X = uploaded_data.iloc[:, :-1]
        #Last column(target variable)
        y = uploaded_data.iloc[:, -1]

        X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2,random_state=42)
        #Train Random Forest model
        rf_model=RandomForestClassifier(n_estimators=100,random_state=42)#number of decision trees
        rf_model.fit(X_train, y_train)
        #Ensure the 'models' directory exists
        if not os.path.exists('models'):
            os.makedirs('models')
        #save the model for prediction
        joblib.dump(rf_model,"models/model.pkl")#pkl=pickel format
        #Redirect to a success page
        flash('Training Successful.You can now proceed to prediction.','success')
        return render_template('train.html')
    except Exception as e:
        flash(f"Error during training: {e}",'danger')
        return redirect(url_for('upload'))

@app.route('/predict',methods=['GET','POST'])
def predict():
    if request.method == 'POST':
        #capture user inputs as a dictionary
        inputs = {
            "Pregnancies": int(request.form['Pregnancies']),
            "Glucose":float(request.form['Glucose']),
            "BloodPressure":float(request.form['BloodPressure']),
            "SkinThickness":float(request.form['SkinThickness']),
            "Insulin":float(request.form['Insulin']),
            "BMI":float(request.form['BMI']),
            "DiabetesPedigreeFunction":float(request.form['DiabetesPedigreeFunction']),
            "Age":int(request.form['Age'])
            }
        #prepare the input values for prediction
        input_values = list(inputs.values())
        #Load the trained model
        model = joblib.load("models/model.pkl")
        prediction = model.predict([input_values])[0]
        #Interpret Prediction Result
        result="Diabetes Detected" if prediction == 1 else "No Diabetes Detected"
        #Pass inputs as a dictionary to result.html
        return render_template('result.html',inputs=inputs,result=result)
    #Render the upload page for GET requests
    return render_template('predict.html')

@app.route('/visualize', methods=['GET', 'POST'])
def visualize():
    global uploaded_data
    if uploaded_data is None:
        flash('No dataset uploaded.', 'warning')
        return redirect(url_for('upload'))

    #Generate plots
    scatter_plot = generate_scatter_plot(uploaded_data)

    return render_template('visualize.html',scatter_plot=scatter_plot,)

def generate_scatter_plot(data):
    #Ensure pregnencies column is integer
    data['Pregnancies'] = data['Pregnancies'].apply(lambda x: int(x) if not pd.isnull(x) else 0)
    #select columns for scatter plot
    numerical_columns = data.select_dtypes(include=['float','int']).columns                                               
    if len(numerical_columns) >= 2:
        plt.figure(figsize=(8, 6))
        #scatterplot
        sns.scatterplot(x=data['Pregnancies'], y=data['Glucose']) #example column; adjust as needed                                          
        plt.title("scatter plot: Pregnancies vs Glucose")
        plt.xlabel("Pregnancies")
        plt.ylabel("Glucose")
        #set x-axis ticks to integers
        max_pregnancies = data['Pregnancies'].max()
        plt.xticks(ticks=np.arange(0, max_pregnancies + 1, 1)) #Range of integers for ticks                                          
        filepath = os.path.join('static', 'images', 'scatter_plot.png')
        plt.savefig(filepath)
        plt.close()
        return filepath
    return None


                                                    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Run the app
    app.run(debug=False, host='0.0.0.0',port = 5000)






















app.secret_key = 'your_secret_key'

### Database configuration
##app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://root:root@localhost/ml_app'
##app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
##
### Initialize SQLAlchemy
##db = SQLAlchemy(app)
##bcrypt = Bcrypt(app)

### Define a database model - User model
##class User(db.Model):
##    id = db.Column(db.Integer, primary_key=True)
##    username = db.Column(db.String(100), unique=True, nullable=False)
##    email = db.Column(db.String(100), unique=True, nullable=False)
##    password = db.Column(db.String(100), nullable=False)


    
@app.route('/')
def index():
    #return "Flask is working!"
    return render_template('index.html')




















@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        #Read the inputs from registration form
        username = request.form['username']#sahana
        email = request.form['email']
        password = request.form['password']

        #Password Encryption
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User(username=username, email=email,
                        password=hashed_password)

        #Saving the user details to database table
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Error: Username or email already exists.', 'danger')

    return render_template('register.html')





if __name__ == '__main__':
    #Ensure tables are created
    with app.app_context():
        db.create_all()
    # Run the app
    app.run(debug=False, host='0.0.0.0',port = 5000)
















    

