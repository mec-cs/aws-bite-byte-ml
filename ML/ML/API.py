import sys
from KNN import KNN
from API_KEY import get_secret
from flask import Flask, request, jsonify

model = KNN()
app = Flask(__name__)

API_KEY = get_secret()

@app.route('/recommend', methods=['GET'])
def recommend():

    request_api_key = request.headers.get('x-api-key')
    if not request_api_key or request_api_key != API_KEY:
        return jsonify({"error": "Unauthorized: Invalid API key"}), 401

    user_id = request.args.get('user_id')
    if user_id is None:
        return jsonify({"error": "user_id parameter is required"}), 400
    
    recommendations = model.main(user_id, 10)
    
    return jsonify(recommendations)

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=port, debug=True)
