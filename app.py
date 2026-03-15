from flask import Flask, request, redirect, render_template_string, session
import sqlite3
import os




app = Flask(__name__)

FILE_NAME = "posts.txt"


















app.secret_key = "huzail_secret"
# File se posts load karne ka function
def load_posts():
    import psycopg2

    conn = psycopg2.connect("postgresql://postgres.fpgvnphpztlgejfkddtf:mahiroshina123@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres")
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, content, created_at FROM posts ORDER BY created_at DESC")
    rows = cursor.fetchall()

    conn.close()

    posts = []

    for row in rows:
        posts.append({
        "id": row[0],
        "title": row[1],
        "content": row[2],
        "time": row[3].strftime("%d %b %Y • %I:%M %p")
        })

    return posts

# File me save karne ka function

def save_post(title, content):
    import psycopg2

    conn = psycopg2.connect("postgresql://postgres.fpgvnphpztlgejfkddtf:mahiroshina123@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO posts (title, content) VALUES (%s, %s)",
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





button{
background:white;
color:black;
padding:10px 20px;
border:none;
border-radius:8px;
cursor:pointer;
font-weight:bold;
}

button:hover{
background:#ddd;
}


.action-box {
    display: inline-block;
    border: 2px solid black;
    background-color: white;
    padding: 5px 10px;
    border-radius: 6px;
}

.action-box a {
    text-decoration: none;
    color: blue;
    margin: 0 5px;
    font-weight: bold;
}



.post-card {
background:#111;
padding:20px;
margin-top:25px;
border-radius:12px;
box-shadow:0 0 10px rgba(255,255,255,0.1);
}



body {
    font-family: 'Playfair Display', serif;
}

 
    
    
</style>




    <title>Huzail's Writing World</title>
</head>
<body>
<div class="container">
    <h1 style="text-align:center;">Welcome to Huzail's Writing World 🌍</h1>

    <form action="/add" method="POST">
        <input type="text" name="title" placeholder="Title" required><br><br>
        <textarea name="content" placeholder="Write here..." required></textarea><br><br>
        <button type="submit">Post</button>
    </form>

<form action="/comment/{{post.id}}" method="POST">
<input type="text" name="comment" placeholder="Write a comment">
<button type="submit">Post</button>
</form>



    <hr>

    {% for post in posts %}

<div class="post-card">
<h2>{{ post.title }}</h2>
<p>{{ post.content }}</p>
<small>Posted on {{ post.time }}</small>
<p>❤️ {{ post.likes }}</p>

<a href="/like/{{post.id}}">
<button>Like</button>
</a>




</div>

<div class="action-box">
<a href="/edit/{{post.id}}">Edit</a> |
<a href="/delete/{{post.id}}" onclick="return confirm('Delete this post?')">Delete</a>
</div>

<hr>

{% endfor %}








</div>
</body>
</html>
"""


login_html = """
<style>
body{
background:black;
color:white;
font-family: 'Playfair Display', serif;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
}

.login-box{
background:#111;
padding:30px;
border-radius:10px;
text-align:center;
}
</style>

<div class="login-box">
<h2>Login</h2>

<form method="POST">
<input type="text" name="username" placeholder="Username"><br><br>
<input type="password" name="password" placeholder="Password"><br><br>
<button type="submit">Login</button>
</form>

</div>
"""

edit_html = """
<h2>Edit Post</h2>

<form method="POST">

<input type="text" name="title" value="{{post[0]}}"><br><br>

<textarea name="content">{{post[1]}}</textarea><br><br>

<button type="submit">Update</button>

</form>
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
    import psycopg2

    conn = psycopg2.connect("postgresql://postgres.fpgvnphpztlgejfkddtf:mahiroshina123@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
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

        if username == "Huzail" and password == "huzail@2468":
            session["logged_in"] = True
            return redirect("/")
    return render_template_string(login_html)




@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/")





@app.route("/delete/<int:id>")
def delete(id):

    if not session.get("logged_in"):
        return redirect("/login")

    import psycopg2

    conn = psycopg2.connect("postgresql://postgres.fpgvnphpztlgejfkddtf:mahiroshina123@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM posts WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    
    if not session.get("logged_in"):
        return redirect("/login")
        
    
    
    import psycopg2

    conn = psycopg2.connect("postgresql://postgres.fpgvnphpztlgejfkddtf:mahiroshina123@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres")
    cursor = conn.cursor()
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        cursor.execute(
            "UPDATE posts SET title=%s, content=%s WHERE id=%s",
            (title, content, id)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    cursor.execute("SELECT title, content FROM posts WHERE id=%s", (id,))
    post = cursor.fetchone()
    conn.close()

    return render_template_string(edit_html, post=post, id=id)



@app.route("/like/<int:id>")
def like_post(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE posts SET likes = likes + 1 WHERE id=%s", (id,))
    
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/comment/<int:id>", methods=["POST"])
def add_comment(id):
    comment = request.form["comment"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO comments (post_id, comment) VALUES (%s,%s)",
        (id, comment)
    )

    conn.commit()
    conn.close()

    return redirect("/")










import os
init_db()
app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
