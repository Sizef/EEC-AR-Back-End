from flask import Flask, jsonify, request
import mysql.connector
import requests
from keras.models import load_model
from keras.preprocessing import image
import numpy as np

# Load the model from the H5 file
param = "model/model.h5"
Model = load_model(param)


# MySQL database configuration
db_config = {   
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'component_infos'
}

app = Flask(__name__)

#Getting data from flutter and processing it
@app.route('/api/data', methods=['POST'])
def get_data():
    try:
        # Access the 'Query' parameter from the request
        query_text = request.form.get('Query')

        print(query_text)

        # Access the uploaded image file
        image_file = request.files['image']

        # Save the image to a specific location (you may want to customize this)
        image_path = f'images/{query_text}.jpg'

        print(image_path)
        print("#########################")
        print("#########################")

        image_file.save(image_path)

        #loading image and calling the model to predict wich objet is in it
        img = image.load_img(image_path , target_size = (200,200))
        X = image.img_to_array(img)
        X = np.expand_dims(X , axis = 0)
        images = np.vstack([X])

        objet = None
        val = Model.predict(images)
        if val == 0 :
            objet = "Central Processing Unit (CPU)"
        elif val == 1 :
            objet = "Random Access Memory (RAM)" 
        else :
            objet = "Not recognized"
        

        if objet == "Not recognized":
            error_data = {"message": "The image is not clear. Please retry"}
            return jsonify(error_data), 200
        else :
            print(f"object founded : {objet}")
            return get_component_info(objet)

    except Exception as e:
        print(f"Error processing image: {str(e)}")
        error_data = {"error": "Failed to process the image"}
        return jsonify(error_data), 500


@app.route('/welcome', methods=['GET'])
def welcome():
    return "welcome to Back End"

@app.route('/get_component_info', methods=['GET'])
def get_component_info(component_name):
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Fetch data from the database based on the component name
        query = "SELECT name , description FROM component WHERE name = %s"
        cursor.execute(query, (component_name,))
        result = cursor.fetchone()

        if result:
            # Convert result to a dictionary for JSON serialization
            component_description = {'name': result[0] , 'description': result[1]}
            return jsonify({'message': component_description}), 200
        else:
            return jsonify({'message': 'Component not found'}), 404


    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Close database connections
        cursor.close()
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0' , port=5000 , threaded=True)
