from flask import Flask, render_template, request, jsonify, redirect, url_for
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize Flask app
app = Flask(__name__)

# Initialize the model
model = genai.GenerativeModel("gemini-1.5-flash")

def get_coach_response(conversation_history):
    prompt = f"""You are an expert fitness coach having a conversation with a client. 
    Based on the conversation history, provide a response that:
    1. Shows empathy and understanding
    2. Asks relevant follow-up questions
    3. Provides brief, helpful advice when appropriate
    4. Maintains a professional yet friendly tone
    5. Gathers important information about their fitness goals and health
    
    If you have gathered enough information (after 5 exchanges), respond with 'GENERATE_PLAN' instead of continuing the conversation.
    
    Previous conversation:
    {conversation_history}
    
    Respond as a fitness coach in a conversational manner."""

    try:
        response = model.generate_content(prompt)
        # Clean up the response
        cleaned_response = response.text.strip()
        # Remove all unwanted symbols
        cleaned_response = cleaned_response.replace('*', '')
        cleaned_response = cleaned_response.replace('|', '')
        cleaned_response = cleaned_response.replace('**', '')
        cleaned_response = cleaned_response.replace('||', '')
        # Format text before colons
        lines = cleaned_response.split('\n')
        formatted_lines = []
        for line in lines:
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    formatted_lines.append(f"{parts[0].strip()}:{parts[1]}")
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append(line)
        return '\n'.join(formatted_lines)
    except Exception as e:
        return f"Error generating response: {str(e)}"

def generate_workout_plan(conversation_history):
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
        return cleaned_response
    except Exception as e:
        return f"Error generating workout plan: {str(e)}"

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
        
        conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        if question_count >= 5:
            # Automatically generate workout plan after 5 questions
            workout_plan = generate_workout_plan(conversation_history)
            return jsonify({
                'success': True,
                'response': workout_plan,
                'generate_plan': True
            })
        else:
            # Continue conversation
            coach_response = get_coach_response(conversation_history)
            return jsonify({
                'success': True,
                'response': coach_response,
                'generate_plan': False
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

if __name__ == '__main__':
    app.run(debug=True)
