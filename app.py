from flask import Flask, request, redirect, render_template_string, session
from functools import wraps
import os
import psycopg2
import bcrypt

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return "Admins only 😎"
        return f(*args, **kwargs)
    return wrapper

# File se posts load karne ka function
def load_posts():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, title, content, likes ,created_at FROM posts ORDER BY created_at DESC")
    rows = cursor.fetchall()

    conn.close()

    posts = []

    for row in rows:
        posts.append({
        "id": row[0],
        "title": row[1],
        "content": row[2],
        "likes":row[3],   
        "time": row[4].strftime("%d %b %Y • %I:%M %p")
        })

    return posts



# File me save karne ka function

def save_post(title, content):

    conn = get_db_connection()
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

.header{
    display:flex;
    justify-content:space-between;
    align-items:center;
    margin-bottom:20px;
}

.settings-btn{
    font-size:28px;
    text-decoration:none;
    background:#111;
    padding:10px 16px;
    border-radius:12px;
    color:white;
    transition:0.3s;
}

.settings-btn:hover{
    background:#333;
    transform:rotate(30deg);
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
    <div class="header">
    <h1>Welcome to Huzail's Writing World 🌍</h1>

    <a href="/settings" class="settings-btn">⚙️</a>
</div>

    <form action="/add" method="POST">
        <input type="text" name="title" placeholder="Title" required><br><br>
        <textarea name="content" placeholder="Write here..." required></textarea><br><br>
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
<a href="/post/{{post.id}}">
    <button>Open Post 💬</button>
</a>

<form action="/comment/{{post.id}}" method="POST">
<input type="text" name="comment" placeholder="Write a comment">
<button type="submit">Comment</button>
</form>


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
<br>
<a href="/signup">Create new account</a>
</div>
"""


signup_html = """
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
<h2>Signup</h2>

<form method="POST">
<input type="text" name="username" placeholder="Username"><br><br>
<input type="password" name="password" placeholder="Password"><br><br>
<button type="submit">Create Account</button>
</form>

<br>
<a href="/login">Login</a>
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


post_page_html = """
<h1>{{post[1]}}</h1>
<p>{{post[2]}}</p>

<hr>
<h2>Comments 💬</h2>

{% for c in comments %}
    <p><b>{{c[0]}}</b>: {{c[1]}}</p>
{% endfor %}

<hr>

{% if session.get("username") %}
<form action="/comment/{{post[0]}}" method="POST">
    <input name="comment" placeholder="Write comment">
    <button>Post Comment</button>
</form>
{% else %}
<p>Login to comment 🙂</p>
{% endif %}

<a href="/">⬅ Back Home</a>
"""



@app.route("/")
def home():
    posts = load_posts()
    return render_template_string(html, posts=posts, user=session.get("username"))

@app.route('/add', methods=['POST'])
@login_required
def add():
    title = request.form['title']
    content = request.form['content']
    save_post(title, content)
    return redirect('/')






def init_db():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        title TEXT,
        content TEXT,
        likes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user'
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER,
    username TEXT, 
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
    
    conn.commit()
    conn.close()

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute(
             "INSERT INTO users (username, password,role) VALUES (%s, %s,%s)",
             (username, hashed.decode('utf-8'),"user")
            )
            conn.commit()
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            return "Username already exists"
        cur.close()
        conn.close()

        return redirect("/login")

    return render_template_string(signup_html)










@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT password_hash , role FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
            session["username"] = username
            session["role"] = user[1]
    # ⭐ ADMIN CHECK ADD KARO
            
            if user[1] == "admin":
                session["is_admin"] = True
            else:
                session["is_admin"] = False
            return redirect("/")
        else:
            return "Wrong username or password"

    return render_template_string(login_html)




@app.route("/logout")
def logout():
    session.clear() # sab session delete
    return redirect("/login")




@app.route("/delete/<int:id>")
@login_required
@admin_required
def delete(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM posts WHERE id=%s", (id,))
    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit(id):
    conn = get_db_connection()
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
@login_required
def like_post(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE posts SET likes = likes + 1 WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect("/")



@app.route("/post/<int:post_id>")
def view_post(post_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # get post
    cur.execute("SELECT * FROM posts WHERE id=%s", (post_id,))
    post = cur.fetchone()
    if not post:
        return "Post not found"
    # get comments of this post
    cur.execute("SELECT username, comment FROM comments WHERE post_id=%s", (post_id,))
    comments = cur.fetchall()

    conn.close()

    return render_template_string(post_page_html, post=post, comments=comments)


@app.route("/comment/<int:post_id>", methods=["POST"])
@login_required
def add_comment_post(post_id):
    comment = request.form["comment"]
    username = session["username"]

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO comments (post_id, username, comment) VALUES (%s,%s,%s)",
        (post_id, username, comment)
    )

    conn.commit()
    conn.close()

    return redirect(f"/post/{post_id}")

def check_profile(username):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM profiles WHERE username=%s", (username,))
    profile = cur.fetchone()
    
    conn.close()
    
    if profile:
        return True
    else:
        return False


@app.route("/settings")
def settings():

    user = session.get("username")   # <-- ek hi session key use karo

    # agar login nahi hai
    if not user:
        return render_template_string("""
        <h1>Settings ⚙️</h1>
        <a href="/login">Login</a><br><br>
        <a href="/signup">Create New Account</a>
        <br><br>
        <a href="/">⬅ Back</a>
        """)

    # login hai → check profile bana hai ya nahi
    profile_exists = check_profile(user)

    # profile bana hua hai
    if profile_exists:
        return render_template_string("""
        <h1>Settings ⚙️</h1>
        <p>Logged in as: <b>{{user}}</b></p>

        <a href="/view_profile">View Profile</a><br><br>
        <a href="/logout">Logout</a>

        <br><br>
        <a href="/">⬅ Back</a>
        """, user=user)

    # login hai but profile nahi bana
    else:
        return render_template_string("""
        <h1>Settings ⚙️</h1>
        <p>Logged in as: <b>{{user}}</b></p>

        <a href="/create_profile">Create Profile</a><br><br>
        <a href="/logout">Logout</a>

        <br><br>
        <a href="/">⬅ Back</a>
        """, user=user)





init_db()
