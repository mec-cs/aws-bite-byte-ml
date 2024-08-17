from flask import Flask, request, jsonify
from KNN import KNN

model = KNN()
app = Flask(__name__)

@app.route('/recommend', methods=['GET'])
def recommend():
    # Get user_id from query parameters
    user_id = request.args.get('user_id')
    
    if user_id is None:
        return jsonify({"error": "user_id parameter is required"}), 400
    
    # Fetch recommendations
    recommendations = model.main(user_id, 10)
    
    return jsonify(recommendations)

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
    app.run(host='0.0.0.0', port=port, debug=True)
