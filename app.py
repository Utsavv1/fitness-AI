from flask import Flask, render_template, request, jsonify, redirect, url_for
from urllib.parse import unquote
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
from googletrans import Translator

# Load environment variables
load_dotenv()

# Configure Google AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Flask app
app = Flask(__name__)

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize translator
translator = Translator()

# Map frontend language codes to Google Translate language codes
LANGUAGE_MAP = {
    'en': 'en',
    'es': 'es',
    'fr': 'fr',
    'hi': 'hi',
    'guj': 'gu',
}

def translate_text(text, target_lang):
    """Translate text to target language using Google Translate"""
    if target_lang == 'en':
        return text
        
    try:
        # Map frontend language code to Google Translate language code
        google_lang = LANGUAGE_MAP.get(target_lang, 'en')
        
        # Split text into chunks of 500 characters
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        translated_chunks = []
        
        for chunk in chunks:
            translator = Translator()
            translated = translator.translate(chunk, dest=google_lang)
            translated_chunks.append(translated.text)
            
        return ' '.join(translated_chunks)
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return text

def split_message(text, max_length=500):
    """Split long messages into chunks of max_length characters"""
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split by sentences first
    sentences = text.split('. ')
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 2 <= max_length:  # +2 for '. '
            current_chunk += sentence + '. '
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def get_coach_response(conversation_history, target_lang='en'):
    # Limit conversation history to last 3 exchanges
    history_lines = conversation_history.split('\n')
    if len(history_lines) > 6:  # Keep last 3 exchanges (6 lines - 3 pairs of user/assistant)
        conversation_history = '\n'.join(history_lines[-6:])

    prompt = f"""You are an expert fitness coach having a conversation with a client. 
    Based on the conversation history, provide a SHORT, SINGLE-LINE response that:
    1. Shows empathy and understanding
    2. Asks ONE relevant follow-up question
    3. Keeps the response under 100 words
    4. Maintains a professional yet friendly tone
    
    IMPORTANT: Your response MUST be a single line and under 100 words.
    If you have gathered enough information (after 5 exchanges), respond with exactly 'GENERATE_PLAN' (no other text).
    
    Previous conversation:
    {conversation_history}
    
    Respond as a fitness coach in a conversational manner."""

    try:
        response = model.generate_content(prompt)
        # Clean up the response
        cleaned_response = response.text.strip()
        # Remove all unwanted symbols and newlines
        cleaned_response = cleaned_response.replace('*', '')
        cleaned_response = cleaned_response.replace('|', '')
        cleaned_response = cleaned_response.replace('**', '')
        cleaned_response = cleaned_response.replace('||', '')
        cleaned_response = cleaned_response.replace('\n', ' ')
        
        # Ensure single line response
        cleaned_response = ' '.join(cleaned_response.split())
        
        # Check if it's time to generate a plan
        if cleaned_response.strip() == 'GENERATE_PLAN':
            return ['GENERATE_PLAN']
        
        # Split response into chunks if needed
        chunks = split_message(cleaned_response)
        
        # Translate each chunk if needed
        if target_lang != 'en':
            translated_chunks = []
            for chunk in chunks:
                translated_chunk = translate_text(chunk, target_lang)
                translated_chunks.append(translated_chunk)
            return translated_chunks
        return chunks
    except Exception as e:
        return [f"Error generating response: {str(e)}"]

def generate_workout_plan(conversation_history, target_lang='en'):
    prompt = f"""Based on the following conversation, create a detailed workout routine:
    
    Conversation History:
    {conversation_history}
    
    Please provide:
    1. A weekly workout schedule
    2. Specific exercises for each day
    3. Sets, reps, and rest periods
    4. Any modifications based on their equipment access
    5. Safety considerations based on their fitness level
    6. Progressive overload recommendations
    7. Warm-up and cool-down suggestions
    
    Format the response in a clear, easy-to-follow structure."""

    try:
        response = model.generate_content(prompt)
        # Clean up the response
        cleaned_response = response.text.strip()
        # Remove all unwanted symbols
        cleaned_response = cleaned_response.replace('*', '')
        cleaned_response = cleaned_response.replace('|', '')
        cleaned_response = cleaned_response.replace('**', '')
        cleaned_response = cleaned_response.replace('||', '')
        # Remove extra spaces
        cleaned_response = cleaned_response.replace('  ', ' ')
        
        # Format text before colons to be bold using HTML tags
        lines = cleaned_response.split('\n')
        formatted_lines = []
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    formatted_lines.append(f"<b>{parts[0].strip()}</b>:{parts[1]}")
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        
        formatted_response = '\n'.join(formatted_lines)
        
        # Split response into chunks if needed
        chunks = split_message(formatted_response)
        
        # Translate each chunk if needed
        if target_lang != 'en':
            translated_chunks = []
            for chunk in chunks:
                translated_chunk = translate_text(chunk, target_lang)
                translated_chunks.append(translated_chunk)
            return translated_chunks
        return chunks
    except Exception as e:
        return [f"Error generating workout plan: {str(e)}"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['GET'])
def chat_page():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        question_count = data.get('question_count', 0)
        target_lang = data.get('language', 'en')  # Default to English if no language is set
        
        # Keep only the last 3 exchanges in the conversation history
        if len(messages) > 6:
            messages = messages[-6:]
        
        conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        # Get coach response
        response_chunks = get_coach_response(conversation_history, target_lang)
        
        # Check if it's time to generate a plan
        if response_chunks[0] == 'GENERATE_PLAN' or question_count >= 5:
            # Generate workout plan
            workout_plan_chunks = generate_workout_plan(conversation_history, target_lang)
            return jsonify({
                'success': True,
                'response': workout_plan_chunks,
                'generate_plan': True,
                'is_chunked': len(workout_plan_chunks) > 1
            })
        else:
            # Continue conversation
            return jsonify({
                'success': True,
                'response': response_chunks,
                'generate_plan': False,
                'is_chunked': len(response_chunks) > 1
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/workout-plan')
def show_workout_plan():
    workout_plan = request.args.get('plan', '')
    return render_template('workout_plan.html', workout_plan=workout_plan)

@app.route('/translate', methods=['POST'])
def translate_endpoint():
    try:
        data = request.json
        text = data.get('text', '')
        target_lang = data.get('target_lang', 'en')
        
        translated_text = translate_text(text, target_lang)
        return jsonify({
            'success': True,
            'translated_text': translated_text
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
