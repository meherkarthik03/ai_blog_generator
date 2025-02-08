from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from transformers import pipeline
import sqlite3  

# Initialize Flask App
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "supersecretkey"  

# Initialize Extensions
CORS(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Load AI Model
blog_generator = pipeline("text-generation", model="EleutherAI/gpt-neo-125M")

# Initialize SQLite Database
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# Create Tables
cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS blogs (id INTEGER PRIMARY KEY, user TEXT, topic TEXT, content TEXT)")
conn.commit()

# ---------------- STEP 1: AUTHENTICATION ----------------

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data["username"]
    password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return jsonify({"message": "User registered successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already exists"}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user and bcrypt.check_password_hash(user[0], password):
        access_token = create_access_token(identity=username)
        return jsonify({"access_token": access_token})
    
    return jsonify({"error": "Invalid credentials"}), 401

# ---------------- STEP 2: BLOG GENERATION ----------------

@app.route("/generate", methods=["POST"])
@jwt_required()
def generate_blog():
    try:
        user = get_jwt_identity()  # Get the logged-in user
        data = request.json
        topic = data.get("topic", "").strip()

        if not topic:
            return jsonify({"error": "Topic is required"}), 400

        # Generate AI-powered blog content
        generated_output = blog_generator(
            topic,
            max_new_tokens=300,
            num_return_sequences=1,
            temperature=0.8,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.3
        )

        generated_blog = generated_output[0]["generated_text"]

        # Save blog to the database
        cursor.execute("INSERT INTO blogs (user, topic, content) VALUES (?, ?, ?)", (user, topic, generated_blog))
        conn.commit()

        return jsonify({"blog": generated_blog, "message": "Blog saved successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- STEP 3: FETCH USER BLOGS ----------------

@app.route("/blogs", methods=["GET"])
@jwt_required()
def get_user_blogs():
    user = get_jwt_identity()
    
    cursor.execute("SELECT topic, content FROM blogs WHERE user=?", (user,))
    blogs = [{"topic": row[0], "content": row[1]} for row in cursor.fetchall()]

    return jsonify({"user": user, "blogs": blogs})

# Run the Flask App
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
