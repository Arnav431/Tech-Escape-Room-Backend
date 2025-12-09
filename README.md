# Quiz Site

## Setup Instructions

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone the repository
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Gemini API Configuration

This project uses Google's Gemini API for advanced answer validation.

#### Setting up the API Key

You have two options for setting the Gemini API key:

1. **Recommended: Environment Variables (Render Deployment)**
   - Go to your Render dashboard
   - Navigate to the service settings
   - Add an environment variable:
     - Key: `GEMINI_API_KEY`
     - Value: Your Gemini API key

2. **Local Development: .env File**
   - Create a `.env` file in the project root
   - Add your API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```
   - Note: NEVER commit the `.env` file to version control
   - A `.env.example` file is provided as a template

### Obtaining an API Key
- Visit: https://makersuite.google.com/app/apikey
- Create a new API key

### Running the Application

1. Set the Gemini API key (see above)
2. Start the backend server:
   ```bash
   python backend.py
   ```
3. Open `index.html` in a web browser

### Deployment Notes
- For Render: Set `GEMINI_API_KEY` in the service environment variables
- For local development: Use the `.env` file
- Ensure the API key is kept secret and not shared publicly

### Troubleshooting
- If no API key is provided, the application will use basic answer validation
- Ensure you have an active internet connection for Gemini API calls

