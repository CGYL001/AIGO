from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return jsonify({"message": "AIgo API服务器正在运行", "status": "ok"})

@app.route("/api/status")
def status():
    return jsonify({"status": "ok", "version": "0.2.0"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
