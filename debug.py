print("STEP 1 OK")

from flask import Flask
print("STEP 2 OK")

app = Flask(__name__)
print("STEP 3 OK")

@app.route("/")
def home():
    print("REQUEST HIT")
    return "FLASK WORKING"

print("STEP 4 OK")

if __name__ == "__main__":
    print("START SERVER")
    app.run(host="0.0.0.0", port=5000, debug=True)