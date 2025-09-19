import openai
from flask import Flask, request

app = Flask(__name__)

# ✅ Put your OpenAI API Key here
openai.api_key = "YOUR_API_KEY_HERE"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Image Generator 🎨</title>
    <style>
        body {
            text-align: center;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #89f7fe, #66a6ff);
            color: #333;
        }
        h1 {
            margin-top: 30px;
        }
        form {
            margin: 20px auto;
        }
        input {
            padding: 10px;
            width: 300px;
            border-radius: 8px;
            border: 1px solid #ccc;
        }
        button {
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            background-color: #007bff;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
        img {
            margin-top: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        }
        .error {
            color: red;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <h1>AI Image Generator 🎨</h1>
    <form method="POST">
        <input type="text" name="prompt" placeholder="Enter your idea..." required>
        <button type="submit">Generate</button>
    </form>
    {error_block}
    {image_block}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    error = None

    if request.method == "POST":
        prompt = request.form["prompt"]
        try:
            response = openai.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="512x512"
            )
            image_url = response.data[0].url
        except Exception as e:
            error = str(e)

    # Build dynamic HTML
    error_block = f'<div class="error">⚠️ {error}</div>' if error else ""
    image_block = ""
    if image_url:
        image_block = f"""
        <h2>Generated Image:</h2>
        <img src="{image_url}" width="400"><br><br>
        <a href="{image_url}" download>
            <button>Download Image</button>
        </a>
        """

    return HTML_PAGE.format(error_block=error_block, image_block=image_block)

if __name__ == "__main__":
    app.run(debug=True)
