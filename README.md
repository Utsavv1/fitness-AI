# AI Fitness Coach

An intelligent fitness coaching application powered by Google's Gemini AI and Streamlit.

## Features

- Personalized workout recommendations
- Nutrition advice and meal planning
- Exercise technique guidance
- Fitness goal setting and tracking
- Recovery and injury prevention advice
- Interactive chat interface

## Setup

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
   To get a Google API key:
   - Go to https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the key to your .env file

## Running the Application

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```
2. Open your web browser and navigate to the URL shown in the terminal (usually http://localhost:8501)

## Usage

1. Type your fitness-related question in the text area
2. Click "Get Advice" to receive personalized recommendations
3. Follow the tips in the sidebar for better responses

## Tips for Better Responses

- Be specific about your goals and current fitness level
- Mention any injuries or limitations
- Specify available equipment
- Ask about proper form for exercises
- Include your dietary preferences and restrictions when asking about nutrition

## Note

This application is for informational purposes only. Always consult with a healthcare professional before starting any new exercise or nutrition program. 