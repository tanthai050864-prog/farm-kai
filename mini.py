from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "OK WORKING"

if __name__ == "__main__":
    print("SERVER START")
app.run(host="0.0.0.0", port=5000, debug=True)