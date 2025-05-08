import logging
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os

# --------------------- Load .env file ---------------------
load_dotenv()  # Load environment variables from the .env file

# --------------------- Logging Setup ---------------------
logging.basicConfig(level=logging.INFO)

# --------------------- Hugging Face API Setup ---------------------
def generate_text_with_hugging_face(prompt):
    """
    Function to generate text using Hugging Face API (GPT-2 model).
    """
    # Fetching Hugging Face API Key from the environment variable
    api_key = os.getenv("HUGGING_FACE_API_KEY")
    
    if not api_key:
        raise ValueError("API key not found! Please set it in the .env file.")
    
    # Hugging Face API URL (GPT-2 model or any other model you'd like to use)
    API_URL = "https://api-inference.huggingface.co/models/gpt2"
    
    # Set headers with the API key
    headers = {"Authorization": f"Bearer {api_key}"}
    
    # Set the prompt in the payload
    payload = {"inputs": prompt}
    
    # Send a POST request to the API
    response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
    
    # Check if the response is successful
    if response.status_code == 200:
        return response.json()  # Return the generated text from the model
    else:
        return f"Error {response.status_code}: {response.text}"  # Return the error message

# --------------------- Calculator Tool ---------------------
def calculate(query):
    """
    A simple calculator to evaluate mathematical expressions in a query.
    """
    try:
        # Extract expression from query (e.g., "calculate 2 + 2")
        expression = query.lower().replace("calculate", "").strip()
        result = eval(expression, {"__builtins__": {}}, {})
        return f"The result is: {result}"
    except Exception as e:
        return f"Error in calculation: {e}"

# --------------------- Dictionary Tool ---------------------
def define(query):
    """
    A simple dictionary tool to fetch word definitions.
    """
    try:
        word = query.lower().split("define")[-1].strip()
        # Fetching definition from a simple placeholder dictionary
        dictionary = {
            "python": "A high-level programming language.",
            "ai": "Artificial Intelligence is the simulation of human intelligence in machines."
        }
        meaning = dictionary.get(word, "Definition not found.")
        return f"Definition of {word}:\n{meaning}"
    except Exception as e:
        return f"Error in lookup: {e}"

# --------------------- Agent Router ---------------------
def route_query(query):
    """
    A function to route queries to different tools (calculator, dictionary, or Hugging Face API).
    """
    query_lower = query.lower()
    logging.info(f"Received query: {query_lower}")
    
    # Routing to calculator if 'calculate' is in the query
    if "calculate" in query_lower:
        logging.info("Routing to Calculator Tool")
        return calculate(query)
    
    # Routing to dictionary if 'define' is in the query
    elif "define" in query_lower:
        logging.info("Routing to Dictionary Tool")
        return define(query)
    
    # Otherwise, routing to Hugging Face API for text generation
    else:
        logging.info("Routing to Hugging Face API for text generation")
        result = generate_text_with_hugging_face(query)
        return result

# --------------------- Flask Setup ---------------------
app = Flask(__name__)

# Route for answering queries
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400
    
    query = data['query']
    logging.info(f"Received query: {query}")
    response = route_query(query)

    return jsonify({"response": response})

# --------------------- Run the Flask App ---------------------
if __name__ == '__main__':
    # Run the Flask app on host 0.0.0.0 to make it publicly accessible
    app.run(debug=True, host='0.0.0.0', port=5000)
