from flask import Flask, render_template_string, request, redirect
import os

app = Flask(__name__)

FILE_NAME = "posts.txt"

# File se posts load karne ka function
def load_posts():
    posts = []
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                title, content = line.strip().split("|||")
                posts.append({"title": title, "content": content})
    return posts

# File me save karne ka function
def save_post(title, content):
    with open(FILE_NAME, "a", encoding="utf-8") as file:
        file.write(f"{title}|||{content}\n")

html = """
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap" rel="stylesheet">
<style>
    body {
        background-color: black;
        color: white;
    }
    
     .container {
    width: 70%;
    margin: auto;
}   
    


.post {
    background-color: #111;
    padding: 15px;
    margin-top: 20px;
    border-radius: 10px;
}





button {
    background-color: white;
    color: black;
    padding: 8px 15px;
    border: none;
    border-radius: 5px;
}






body {
    font-family: 'Playfair Display', serif;
}

    
    
    
</style>




    <title>Huzail's Writing World</title>
</head>
<body>
<div class="container">
    <h1>Welcome to Huzail's Writing World 🌍</h1>

    <form action="/add" method="POST">
        <input type="text" name="title" placeholder="Title" required><br><br>
        <textarea name="content" placeholder="Write here..." required></textarea><br><br>
        <button type="submit">Post</button>
    </form>

    <hr>

    {% for post in posts %}
        <h2>{{ post.title }}</h2>
        <p>{{ post.content }}</p>
        <hr>
    {% endfor %}
    
    









</div>
</body>
</html>
"""











@app.route('/')
def home():
    posts = load_posts()
    return render_template_string(html, posts=posts)

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    content = request.form['content']
    save_post(title, content)
    return redirect('/')

app.run(host='0.0.0.0', port=5000)