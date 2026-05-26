# 🌙 ReadmeNeko 🐾

**ReadmeNeko** is a dynamic tool that generates your GitHub profile stats with a dreamy aesthetic, a starry night sky, and adorable kitty paws. 

Instead of the usual gray counters, ReadmeNeko turns your metrics (Repositories, Followers, etc.) into a colorful vector image (SVG) generated on the fly, ready to give a unique and personal touch to your `README.md`.

## ✨ Features

* 🐈 **Eye-catching Design:** A dark night theme enriched with a crescent moon, pastel stars, and cat paw prints.
* ⚡ **Real-Time Generation:** Vector images (SVG) dynamically rendered on every request.
* 🐍 **Simple and Lightweight:** Built entirely in Python using the Flask micro-framework.
* 🔄 **Anti-Caching:** HTTP headers configured to prevent GitHub from displaying outdated, cached stats.

## 🛠️ Tech Stack

* **Python 3**
* **Flask** (Web Framework)
* **Requests** (HTTP Library)
* **GitHub REST API**

## 🚀 Getting Started (Local Development)

If you want to clone the project to test it or tweak the design on your machine:

1. **Clone the repository:**
```bash
   git clone [https://github.com/YOUR_USERNAME/ReadmeNeko.git](https://github.com/YOUR_USERNAME/ReadmeNeko.git)
   cd ReadmeNeko
Install dependencies:
Using a virtual environment (venv) is recommended.

Bash
   pip install flask requests
Set up your GitHub Token:

Generate a Personal Access Token (PAT) on GitHub (with read-only permissions).

Insert the token into the app.py file at the line GITHUB_TOKEN = "YOUR_TOKEN_HERE".

Run the server:

Bash
   python app.py
Admire the result:
Open your browser and go to http://127.0.0.1:5000/api?username=YOUR_USERNAME