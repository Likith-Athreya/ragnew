import logging
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from waitress import serve

# --------------------- Load .env file ---------------------
load_dotenv()  # Load environment variables from the .env file

# --------------------- Logging Setup ---------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --------------------- Hugging Face API Setup ---------------------
def generate_text_with_hugging_face(prompt):
    """
    Function to generate text using Hugging Face API (GPT-2 model).
    """
    api_key = os.getenv("HUGGING_FACE_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found! Please set it in the .env file.")
    
    API_URL = "https://api-inference.huggingface.co/models/gpt2"
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    payload = {"inputs": prompt}
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Will raise an exception for 4xx or 5xx status codes
        return response.json()  # Return the generated text from the model
    except requests.exceptions.RequestException as e:
        logging.error(f"Error while calling Hugging Face API: {e}")
        return f"Error while processing the request: {e}"

# --------------------- Calculator Tool ---------------------
def calculate(query):
    """
    A simple calculator to evaluate mathematical expressions in a query.
    """
    try:
        expression = query.lower().replace("calculate", "").strip()
        result = eval(expression, {"__builtins__": {}}, {})
        return f"The result is: {result}"
    except Exception as e:
        logging.error(f"Error in calculation: {e}")
        return f"Error in calculation: {e}"

# --------------------- Dictionary Tool ---------------------
def define(query):
    """
    A simple dictionary tool to fetch word definitions.
    """
    try:
        word = query.lower().split("define")[-1].strip()
        dictionary = {
            "python": "A high-level programming language.",
            "ai": "Artificial Intelligence is the simulation of human intelligence in machines."
        }
        meaning = dictionary.get(word, "Definition not found.")
        return f"Definition of {word}:\n{meaning}"
    except Exception as e:
        logging.error(f"Error in lookup: {e}")
        return f"Error in lookup: {e}"

# --------------------- Agent Router ---------------------
def route_query(query):
    """
    A function to route queries to different tools (calculator, dictionary, or Hugging Face API).
    """
    query_lower = query.lower()
    
    if "calculate" in query_lower:
        logging.info("Routing to Calculator Tool")
        return calculate(query)
    
    elif "define" in query_lower:
        logging.info("Routing to Dictionary Tool")
        return define(query)
    
    else:
        logging.info("Routing to Hugging Face API for text generation")
        return generate_text_with_hugging_face(query)

# --------------------- Flask Setup ---------------------
app = Flask(__name__)
app.config['DEBUG'] = os.getenv("FLASK_DEBUG", "False").lower() == "true"

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    query = data['query']
    response = route_query(query)

    return jsonify({"response": response})

# --------------------- Ping Route (Health Check) ---------------------
@app.route('/ping', methods=['GET'])
def ping():
    """
    A simple health check endpoint to ensure the application is up and running.
    """
    return jsonify({"status": "ok"})

# --------------------- Run the Flask App ---------------------
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)
