# run.py
import os
from app import create_app

# Create the Flask app instance
app = create_app()

if __name__ == '__main__':
    # Get the port from environment variable (for deployment) or default to 5000 (local)
    port = int(os.environ.get('PORT', 5000))
    # Run the app, binding to 0.0.0.0 to allow external access
    app.run(host='0.0.0.0', port=port, debug=True)  # Set debug=False for production