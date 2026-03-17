import os
from flask import Flask, request
import openai
import logging

# -------------------------------
# Configuration
# -------------------------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not set. Set it via environment variable.")
    OPENAI_API_KEY = ""

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Allowed image sizes
ALLOWED_SIZES = {"256x256", "512x512", "1024x1024"}
DEFAULT_SIZE = "512x512"

# Prompt length limits
MIN_PROMPT_LEN = 5
MAX_PROMPT_LEN = 500



# -------------------------------
# HTML Template
# -------------------------------
HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>AI Image Generator \U0001F3A8</title>
    <style>
        body {
            text-align: center;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #89f7fe, #66a6ff);
            color: #333;
            margin: 0;
            padding: 20px;
        }
        h1 {
            margin-top: 30px;
        }
        form {
            margin: 20px auto;
        }
        input[type="text"] {
            padding: 10px;
            width: 300px;
            border-radius: 8px;
            border: 1px solid #ccc;
        }
        select {
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #ccc;
            margin-left: 10px;
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
        .error {
            color: red;
            margin-top: 15px;
        }
        .history {
            margin: 20px auto;
            padding: 15px;
            background: rgba(255,255,255,0.3);
            border-radius: 8px;
            max-width: 400px;
        }
        .history img {
            width: 100px;
            height: 100px;
            object-fit: cover;
            border-radius: 8px;
            margin: 5px;
        }
    </style>
</head>
<body>
    <h1>AI Image Generator \U0001F3A8</h1>
    <form method="POST">
        <input type="text" name="prompt" placeholder="Enter your idea..." required>
        <select name="size">
            <option value="256x256">256x256</option>
            <option value="512x512" selected>512x512</option>
            <option value="1024x1024">1024x1024</option>
        </select>
        <button type="submit">Generate</button>
    </form>
    {error_block}
    {image_block}
    {history_block}
</body>
</html>"""



# -------------------------------
# Routes
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    error = ""
    image_url = ""
    size = DEFAULT_SIZE

    # Load history from session
    history = session_history.get("history", [])

    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        size = request.form.get("size", DEFAULT_SIZE)

        # Validate size
        if size not in ALLOWED_SIZES:
            size = DEFAULT_SIZE

        # Validate prompt
        if not prompt:
            error = "Please enter a prompt."
        elif len(prompt) < MIN_PROMPT_LEN:
            error = f"Prompt must be at least {MIN_PROMPT_LEN} characters."
        elif len(prompt) > MAX_PROMPT_LEN:
            error = f"Prompt must be at most {MAX_PROMPT_LEN} characters."
        elif not OPENAI_API_KEY:
            error = "API key not configured. Set OPENAI_API_KEY environment variable."
        else:
            logging.info(f"Generating image for prompt: {prompt[:50]}... (size: {size})")
            try:
                response = openai.images.generate(
                    prompt=prompt,
                    size=size,
                    n=1
                )
                image_url = response.data[0].url
                logging.info(f"Image generated successfully: {image_url[:60]}...")
                session_history["history"] = history[:2] + [image_url]
            except openai.error.InvalidRequestError as e:
                logging.error(f"Invalid request error: {e}")
                error = "Invalid prompt. Please try a different description."
            except openai.error.AuthenticationError as e:
                logging.error(f"Authentication error: {e}")
                error = "Invalid API key. Please check your OPENAI_API_KEY."
            except openai.error.RateLimitError as e:
                logging.error(f"Rate limit error: {e}")
                error = "Rate limit exceeded. Please try again later."
            except openai.error.APIConnectionError as e:
                logging.error(f"Connection error: {e}")
                error = "Network error. Please check your connection."
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                error = "An error occurred. Please try again."

    # Build dynamic HTML blocks
    error_block = f'<div class="error">\U0001F6A8 {error}</div>' if error else ""

    image_block = ""
    if image_url:
        image_block = f"""
        <h2>Generated Image:</h2>
        <img src="{image_url}" alt="Generated Image" style="width:400px;border-radius:8px;"><br><br>
        <a href="{image_url}" download target="_blank">
            <button>Download Image</button>
        </a>
        """

    history_block = ""
    if history:
        imgs = "".join(f'<a href="{url}" target="_blank"><img src="{url}" alt="History"></a>' for url in history)
        history_block = f"""
        <div class="history">
            <h3>Recent Generations:</h3>
            {imgs}
        </div>
        """

    return HTML_PAGE.format(error_block=error_block, image_block=image_block, history_block=history_block)


# -------------------------------
# Session History Store
# -------------------------------
session_history = {"history": []}


# -------------------------------
# Entry Point
# -------------------------------
if __name__ == "__main__":
    DEBUG = os.environ.get("DEBUG", "False").lower() in ("true", "1", "yes")
    print(f"Starting AI Image Generator (Debug: {DEBUG})")
    print("Make sure OPENAI_API_KEY is set in environment variables.")
    app.run(debug=DEBUG)
