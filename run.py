from app import create_app
import os

# Create the Flask application
app = create_app()

# Ensure SECRET_KEY is properly set
secret_key = os.environ.get("SECRET_KEY")
if not secret_key or secret_key == "your-secret-key":
    print("⚠️ WARNING: SECRET_KEY is not set or using default. Make sure to set it in your environment variables.")
    secret_key = "fallback-secret-key"  # You can change this to something random

app.secret_key = secret_key

# Debugging: Print SECRET_KEY to verify
print(f"🔑 SECRET_KEY set: {app.secret_key}")

if __name__ == '__main__':
    # Get the port from Render (default to 10000 if not found)
    port = int(os.environ.get("PORT", 10000))

    # Run the app on 0.0.0.0 to accept external requests
    app.run(host="0.0.0.0", port=port)
