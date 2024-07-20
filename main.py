from flask import Flask, request, jsonify
from groq import Groq
from PIL import Image
import pytesseract
import io
import os

app = Flask(__name__)

# Set up Groq client
api_key = "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"
client = Groq(api_key=api_key)

@app.route('/')
def index():
    with open('index.html', 'r') as file:
        return file.read()

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Read the image file
        image_data = file.read()
        
        # Use pytesseract to extract text from the image
        image = Image.open(io.BytesIO(image_data))
        user_prompt = pytesseract.image_to_string(image)
        
        # Construct the full prompt
        full_prompt = f"""
        Generate LaTeX code to represent the following mathematical expression:
        {user_prompt}
        
        Please follow these guidelines:
        1. Ensure the LaTeX code is complete and can be compiled.
        2. Use appropriate mathematical environments (e.g., equation, align) as needed.
        3. If there are multiple equations, consider using the 'align' environment.
        4. Include any necessary LaTeX packages in the preamble.
        5. If the image contains any special symbols or notations, use the correct LaTeX commands to represent them.
        6. Use just what's in the text; don't add something new that doesn't exist in the text.
        
        Provide the complete LaTeX code, including the document class and any necessary packages.
        """
        
        # Create the completion request
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                },
                {
                    "role": "assistant",
                    "content": "Here is a response to your prompt:"
                }
            ],
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        
        # Extract the generated LaTeX code from the response
        latex_code = completion.choices[0].message.content
        
        return jsonify({'latex_code': latex_code})

if __name__ == '__main__':
    app.run(debug=True)
