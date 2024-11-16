from flask import Flask, request, jsonify, render_template
import pickle  # Importing pickle to load the model
import os

app = Flask(__name__)

# Global variable to hold the model
model = None

print(os.getcwd())
# Load the model when the application starts
def load_model():
    global model
    try:
        model_path = os.path.join(os.getcwd(), 'liver/liver_disease_prediction.pkl')  # Ensure the correct path
        print("Model path:", model_path)  # Debug: Print model path

        # Check if the model file exists
        if not os.path.exists(model_path):
            print(f"Model file not found at: {model_path}")
        else:
            # Load the model using pickle
            with open(model_path, 'rb') as model_file:
                model = pickle.load(model_file)
                print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model with pickle: {str(e)}")
        model = None  # Set model to None if loading fails

# Call this function to load the model when the app starts
load_model()

# Function to make a prediction based on the input data
def predict_liver_disease(age, gender, tot_bilirubin, direct_bilirubin, tot_proteins, 
                           albumin, ag_ratio, sgpt, sgot, alkphos):
    try:
        if model is None:
            return "Error in prediction: Model not loaded!"
        
        # One-hot encoding for gender
        gender_encoded = [1, 0] if gender == 'male' else [0, 1]  # One-hot encoding for male/female
        
        # Prepare the input data in the same format as the training data
        input_data = [
            [age, tot_bilirubin, direct_bilirubin, tot_proteins, albumin, 
             ag_ratio, sgpt, sgot, alkphos] + gender_encoded
        ]

        # Predict using the trained model
        prediction = model.predict(input_data)

        # Return a meaningful prediction result
        return "Liver Disease Present" if prediction[0] == 1 else "Liver Disease Absent"
    
    except Exception as e:
        return f"Error in prediction: {str(e)}"

# Home route to serve the HTML page
@app.route('/')
def home():
    return render_template('liver_p1.html')

# API route to handle prediction (POST request)
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse the form data sent from the frontend (ensure JSON payload)
        data = request.get_json()  # Using get_json() for incoming JSON data
        age = float(data.get('age'))
        gender = data.get('gender')
        tot_bilirubin = float(data.get('tot_bilirubin'))
        direct_bilirubin = float(data.get('direct_bilirubin'))
        tot_proteins = float(data.get('tot_proteins'))
        albumin = float(data.get('albumin'))
        ag_ratio = float(data.get('ag_ratio'))
        sgpt = float(data.get('sgpt'))
        sgot = float(data.get('sgot'))
        alkphos = float(data.get('alkphos'))

        # Call the prediction function and get the result
        prediction = predict_liver_disease(
            age, gender, tot_bilirubin, direct_bilirubin, 
            tot_proteins, albumin, ag_ratio, sgpt, sgot, alkphos
        )

        # Return the prediction as a JSON response to the frontend
        return jsonify({"prediction": prediction})

    except Exception as e:
        return jsonify({"error": str(e)})

# Route to display the result (GET request)
@app.route('/result')
def result():
    prediction = request.args.get('prediction')  # Get the prediction result from the query parameter
    return render_template('liver_p2.html', prediction=prediction)

# Route to display the doctors(GET request)
@app.route('/doctors')
def doctors():
    return render_template('doctor_details.html')

if __name__ == '__main__':
    app.run(debug=True)