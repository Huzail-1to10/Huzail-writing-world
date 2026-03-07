from flask import session
from flask import Flask, render_template_string, request, redirect
import sqlite3
import os




app = Flask(__name__)

FILE_NAME = "posts.txt"



SELECT id, title, content FROM posts


rows = cursor.fetchall()





row[0] = id
row[1] = title
row[2] = content








app.secret_key = "huzail_secret"
# File se posts load karne ka function
def load_posts():
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()

    cursor.execute("SELECT title, content FROM posts")
    rows = cursor.fetchall()

    conn.close()

    posts = []
    for row in rows:
        posts.append({
    "id": row[0],
    "title": row[1],
    "content": row[2]
})

    return posts

# File me save karne ka function

def save_post(title, content):
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO posts (title, content) VALUES (?, ?)",
        (title, content)
    )

    conn.commit()
    conn.close()


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

 <a href="/edit/{{post.id}}">Edit</a>
<a href="/delete/{{post.id}}">Delete</a>   
    
    
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






def init_db():
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT
    )
    """)

    conn.commit()
    conn.close()










@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["logged_in"] = True
            return redirect("/")
    return render_template_string(login_html)




@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/")





@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM posts WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")



@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect("posts.db")
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        cursor.execute(
            "UPDATE posts SET title=?, content=? WHERE id=?",
            (title, content, id)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    cursor.execute("SELECT title, content FROM posts WHERE id=?", (id,))
    post = cursor.fetchone()
    conn.close()

    return render_template_string(edit_html, post=post, id=id)







import os
init_db()
app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
