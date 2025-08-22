from flask import Flask, render_template, jsonify
import random
import string
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

def generate_password(length=12, special_chars=3):
    """Generate a password with specified length and number of special characters."""
    if length < 4:
        length = 12
    if special_chars > length:
        special_chars = length // 3
    
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Ensure minimum requirements
    password_chars = []
    
    # Add required special characters
    for _ in range(special_chars):
        password_chars.append(random.choice(special))
    
    # Add at least one uppercase, one lowercase, and one digit
    password_chars.append(random.choice(uppercase))
    password_chars.append(random.choice(lowercase))
    password_chars.append(random.choice(digits))
    
    # Fill the rest randomly from all character sets
    remaining_length = length - len(password_chars)
    all_chars = lowercase + uppercase + digits + special
    
    for _ in range(remaining_length):
        password_chars.append(random.choice(all_chars))
    
    # Shuffle the password characters
    random.shuffle(password_chars)
    
    return ''.join(password_chars)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/generate', methods=['GET'])
def generate():
    """API endpoint to generate a new password."""
    password = generate_password(length=12, special_chars=3)
    return jsonify({'password': password})

@app.route('/health')
def health():
    """Health check endpoint for Render."""
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
