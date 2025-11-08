from flask import Flask, jsonify, request, render_template 
# You need to create a 'templates' folder for Flask to find the HTML, 
# OR use a simple redirect to the index.html file location.
# For maximum simplicity, let's just serve the index file directly for now, 
# which requires using Flask's send_static_file or using a templates folder.

# HACKATHON SIMPLICITY: Let's use the simplest method by using a dedicated templates folder.

app = Flask(__name__)

@app.route('/')
def index():
    # To use render_template, you must move your index.html into a new folder called 'templates'
    return render_template('index.html') 

@app.route('/generate_content', methods=['POST'])
def generate_content():
    # This is where your AI logic will go!
    data = request.get_json()
    business_description = data.get('description', 'No description provided')
    
    # Placeholder for the hackathon
    return jsonify({
        "status": "success",
        "ideas": [
            f"Idea 1 (Social Post): Use an image of a happy dog and the caption: 'Sustainability never felt so soft! Meet our new eco-toy line.'",
            f"Idea 2 (Blog Post): 'Top 5 Eco-Friendly Dog Products for Urban Living' - Mentioning your product.",
            f"Idea 3 (Video Script): A 15-second TikTok showing a quick, fun way to recycle old toys, with a call to action to buy your new product.",
            f"Analysis received: {business_description[:30]}..." # Shows the AI received the data
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)