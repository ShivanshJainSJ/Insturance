import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

# Function to get a response from the Gemini API
def get_chatbot_response(user_input):
    response = genai.GenerativeModel('gemini-pro').generate_content(user_input)
    return response.text

# Main function to run the text-based assistant
def main():
    print("Hello! I am your text-based assistant. How can I assist you today?")
    
    while True:
        command = input("You: ")
        if command.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break
        else:
            # Get response from the chatbot
            response = get_chatbot_response(command)
            print(f"Assistant: {response}")

if __name__ == "__main__":
    main()