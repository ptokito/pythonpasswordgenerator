from flask import Flask, render_template, request, jsonify
import random
import string

# Create Flask app instance - templates folder is used by default
app = Flask(__name__)

def generate_password(length=12, include_uppercase=True, include_lowercase=True, 
                     include_numbers=True, include_symbols=True):
    """
    Generate a random password with specified criteria.
    
    Args:
        length (int): Length of the password
        include_uppercase (bool): Include uppercase letters
        include_lowercase (bool): Include lowercase letters  
        include_numbers (bool): Include numbers
        include_symbols (bool): Include symbols
    
    Returns:
        str: Generated password
    """
    if length < 4:
        length = 4  # Minimum length for security
    
    characters = ""
    required_chars = []
    
    if include_uppercase:
        characters += string.ascii_uppercase
        required_chars.append(random.choice(string.ascii_uppercase))
    
    if include_lowercase:
        characters += string.ascii_lowercase
        required_chars.append(random.choice(string.ascii_lowercase))
    
    if include_numbers:
        characters += string.digits
        required_chars.append(random.choice(string.digits))
    
    if include_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        required_chars.append(random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
    
    if not characters:
        # Default to all character types if none selected
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        required_chars = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice("!@#$%^&*()_+-=[]{}|;:,.<>?")
        ]
    
    # Fill remaining length with random characters
    remaining_length = length - len(required_chars)
    password_chars = required_chars + [random.choice(characters) for _ in range(remaining_length)]
    
    # Shuffle to avoid predictable patterns
    random.shuffle(password_chars)
    
    return ''.join(password_chars)

@app.route('/')
def index():
    """Render the main password generator page."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "password-generator"})

@app.route('/generate', methods=['POST'])
def generate():
    """Generate password based on user criteria."""
    try:
        data = request.get_json()
        
        # Get parameters with defaults
        length = int(data.get('length', 12))
        include_uppercase = data.get('include_uppercase', True)
        include_lowercase = data.get('include_lowercase', True)
        include_numbers = data.get('include_numbers', True)
        include_symbols = data.get('include_symbols', True)
        
        # Validate length
        if length < 4:
            return jsonify({"error": "Password length must be at least 4 characters"}), 400
        if length > 128:
            return jsonify({"error": "Password length cannot exceed 128 characters"}), 400
        
        # Generate password
        password = generate_password(
            length=length,
            include_uppercase=include_uppercase,
            include_lowercase=include_lowercase,
            include_numbers=include_numbers,
            include_symbols=include_symbols
        )
        
        return jsonify({
            "password": password,
            "length": len(password),
            "criteria": {
                "uppercase": include_uppercase,
                "lowercase": include_lowercase,
                "numbers": include_numbers,
                "symbols": include_symbols
            }
        })
        
    except ValueError as e:
        return jsonify({"error": "Invalid input parameters"}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
