from flask import Flask, request, redirect, render_template, render_template_string, session
from functools import wraps
from werkzeug.utils import secure_filename
import os
import psycopg2
import bcrypt

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_SAMESITE="Lax"
)
DATABASE_URL = "postgresql://neondb_owner:npg_EIa59FXUGpsc@ep-cold-wave-aqj41kf4-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"


UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return render_template_string(login_warning_html)
        print("Role set to:", session["role"])   # verify yahan
        return f(*args, **kwargs)
    return wrapper

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print("Session data:", session)        # pura session dekho
        print("Role in session:", session.get("role"))  # role specifically dekho
        if session.get("role") != "admin":
            return "Admins only 😎"
        return f(*args, **kwargs)
    return wrapper

# File se posts load karne ka function
def load_posts():
    search = request.args.get("search")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, content, likes ,created_at, image_url FROM posts ORDER BY created_at DESC")  
    rows = cursor.fetchall()  

    conn.close()  

    posts = []  

    for row in rows:  
        posts.append({  
        "id": row[0],  
        "title": row[1],  
        "content": row[2],  
        "likes":row[3],     
        "time": row[4].strftime("%d %b %Y • %I:%M %p"),
        "image": row[5]
        })  

    return posts

# File me save karne ka function

def save_post(title, content):

    conn = get_db_connection()
    cursor = conn.cursor()
    username = session["username"]
    user_id = session["user_id"]  # future ke liye

    cursor.execute(
        """
        INSERT INTO posts (title, content, username, user_id)
        VALUES (%s, %s, %s, %s)
        """,
        (title, content, username, user_id)
        )

    conn.commit()
    conn.close()
from datetime import datetime, timezone

def time_ago(timestamp):
    now = datetime.now(timezone.utc)
    diff = now - timestamp.replace(tzinfo=timezone.utc)

    seconds = diff.total_seconds()

    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        mins = int(seconds // 60)
        return f"{mins} min ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hours ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} days ago"
    elif seconds < 2592000:
        weeks = int(seconds // 604800)
        return f"{weeks} weeks ago"
    else:
        months = int(seconds // 2592000)
        return f"{months} months ago"




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
<input type="email" name="email" placeholder="Email" required>
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

<style>
body{
    font-family: Arial;
    margin:0;
    background:#fafafa;
}

/* Top header */
.topbar{
    position:sticky;
    top:0;
    background:white;
    padding:15px;
    border-bottom:1px solid #ddd;
    display:flex;
    justify-content:space-between;
    align-items:center;
    font-size:22px;
    font-weight:bold;
}

.close{
    font-size:28px;
    text-decoration:none;
    color:black;
}

/* Post */
.container{
    padding:20px;
}

.comment{
    margin-bottom:18px;
}

.meta{
    font-size:14px;
    color:gray;
}

form{
    position:fixed;
    bottom:0;
    width:100%;
    background:white;
    padding:10px;
    border-top:1px solid #ddd;
}

input{
    width:75%;
    padding:10px;
}

button{
    padding:10px 20px;
}
</style>


<!-- TOP BAR -->
<div class="topbar">
    <div>Comments {{comment_count}}</div>
    <a href="/" class="close">✕</a>
</div>


<div class="container">

<h1>{{post[1]}}</h1>
<p>{{post[2]}}</p>

<hr>

{% for c in comments %}
<div class="comment">
    <div class="meta">
        <b>{{c[0]}}</b> • {{c[2]}}
    </div>
    <div>{{c[1]}}</div>
</div>
{% endfor %}

</div>


{% if session.get("username") %}
<form action="/comment/{{post[0]}}" method="POST">
    <input name="comment" placeholder="Write comment..." required>
    <button>Send</button>
</form>
{% endif %}

"""


login_warning_html = """
<style>
body{
background:black;
color:white;
display:flex;
justify-content:center;
align-items:center;
height:100vh;
font-family: 'Playfair Display', serif;
text-align:center;
}

.box{
background:#111;
padding:40px;
border-radius:15px;
box-shadow:0 0 15px rgba(255,255,255,0.2);
}

h1{
font-size:50px;
margin-bottom:20px;
}

a{
text-decoration:none;
color:black;
background:white;
padding:12px 25px;
border-radius:10px;
font-weight:bold;
}
</style>

<div class="box">
<h1>🔒 Please Login</h1>
<p>You must login before posting, liking or commenting.</p>
<br>
<a href="/login">Go to Login</a>
</div>
"""
profile_html = """

<style>
body{
    font-family:Arial, sans-serif;
    background:white;
    margin:0;
}

/* Top Bar */
.topbar{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:15px;
    font-size:28px;
}

.topbar a{
    text-decoration:none;
    color:black;
}

/* Profile Header */
.profile-header{
    display:flex;
    align-items:center;
    padding:20px;
}

.profile-pic{
    width:90px;
    height:90px;
    border-radius:50%;
    object-fit:cover;
    margin-right:20px;
}

.profile-info h1{
    margin:0;
    font-size:38px;
}

.username{
    color:gray;
    font-size:18px;
}

/* Tabs */
.tabs{
    text-align:center;
    margin-top:20px;
    border-bottom:1px solid #ddd;
}

.tabs h2{
    display:inline-block;
    padding:10px 30px;
    border-bottom:3px solid black;
}

/* Posts */
.posts{
    padding:20px;
}

.post-card{
    background:#f5f5f5;
    padding:15px;
    margin-bottom:15px;
    border-radius:10px;
}

.post-card h3{
    margin-top:0;
}
</style>


<div class="topbar">
    <a href="/">←</a>
    <div>⋮</div>
</div>


<div class="profile-header">

    <img src="{{profile_image}}" class="profile-pic">

    <div class="profile-info">
        <h1>{{profile_name}}</h1>
        <div class="username">@{{username}}</div>
    </div>

</div>


<div class="tabs">
    <h2>Posts</h2>
</div>


<div class="posts">

{% for post in posts %}
<div class="post-card">
    <h3>{{post.title}}</h3>
    <p>{{post.content}}</p>
</div>
{% endfor %}

</div>

"""
@app.route("/")
def home():

    search = request.args.get("search")

    conn = get_db_connection()
    cur = conn.cursor()

    if search:
        cur.execute(
            """
            SELECT id,title,content,likes,created_at
            FROM posts
            WHERE title ILIKE %s
            ORDER BY created_at DESC
            """,
            (f"%{search}%",)
        )
    else:
        cur.execute(
            """
            SELECT id,title,content,likes,created_at
            FROM posts
            ORDER BY created_at DESC
            """
        )

    rows = cur.fetchall()
    conn.close()

    posts = []

    for row in rows:
        posts.append({
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "likes": row[3],
            "time": row[4].strftime("%d %b %Y • %I:%M %p")
        })

    return render_template("home.html", posts=posts)

@app.route('/add', methods=['POST'])
@login_required
def add():

    title = request.form['title']
    content = request.form['content']

    image = request.files['image']

    image_path = None

    if image and image.filename:
        filename = secure_filename(image.filename)

        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )

        image.save(image_path)

        image_path = "/" + image_path

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO posts
        (title, content, image_url)
        VALUES (%s,%s,%s)
        """,
        (title, content, image_path)
    )

    conn.commit()
    conn.close()

    return redirect("/")




def init_db():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id SERIAL PRIMARY KEY,
        title TEXT,
        content TEXT,
        likes INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        image_url TEXT,
        username TEXT,
        user_id INTEGER REFERENCES users(id)
    )
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP ,
    is_active BOOLEAN DEFAULT TRUE 
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER REFERENCES posts(id) ON DELETE CASCADE,
    username TEXT,
    
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id)
)
""")
    cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    bio TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES users(id),
    profile_name TEXT NOT NULL,
    profile_image TEXT 
)
""")
    
    conn.commit()
    conn.close()

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]  
        password = request.form["password"]

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
INSERT INTO users (username, email, password_hash, role)
VALUES (%s, %s, %s, %s)
""", (username, email, hashed.decode('utf-8'), "user"))
            conn.commit()
        except psycopg2.errors.UniqueViolation as e:
            conn.rollback()
            if "email" in str(e):
                return "Email already exists"
            return "Username already exists"
        except Exception as e:
            conn.rollback()
            return str(e)
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

    # get comments
    cur.execute("""
        SELECT username, comment, created_at 
        FROM comments 
        WHERE post_id=%s 
        ORDER BY created_at DESC
    """, (post_id,))
    comments = cur.fetchall()
    comments_with_time = []
    for c in comments:
        username, comment, created_at = c
        comments_with_time.append(
            (username, comment, time_ago(created_at))
        )

    comment_count = len(comments_with_time)

    conn.close()

    return render_template_string(
        post_page_html,
        post=post,
        comments=comments_with_time,
        session=session,
        comment_count=comment_count
    )
    


@app.route("/comment/<int:post_id>", methods=["POST"])
@login_required
def add_comment_post(post_id):
    comment = request.form["comment"].strip()
    if not comment:
        return redirect(f"/post/{post_id}")
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
        <a href="/delete_account"
   onclick="return confirm('Are you sure? This account will be permanently deleted.')">
Delete Account 🗑️
</a>
 
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
        <a href="/delete_account"
   onclick="return confirm('Are you sure? This account will be permanently deleted.')">
Delete Account 🗑️
</a>

        <br><br>
        <a href="/">⬅ Back</a>
        """, user=user)

@app.route("/delete_account", methods=["GET","POST"])
@login_required
def delete_account():
    username = session["username"]

    conn = get_db_connection()
    cur = conn.cursor()

    # profile delete
    cur.execute(
        "DELETE FROM profiles WHERE username=%s",
        (username,)
    )

    # comments delete
    cur.execute(
        "DELETE FROM comments WHERE username=%s",
        (username,)
    )

    # user delete
    cur.execute(
        "DELETE FROM users WHERE username=%s",
        (username,)
    )

    conn.commit()
    conn.close()

    session.clear()

    return redirect("/")

@app.route("/profile/<username>")
def profile(username):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT profile_name, profile_image FROM profiles WHERE username=%s",
        (username,)
    )
    profile = cur.fetchone()

    cur.execute(
        "SELECT title, content FROM posts WHERE username=%s ORDER BY id DESC",
        (username,)
    )
    posts = cur.fetchall()

    conn.close()

    return render_template_string(
        profile_html,
        profile_name=profile[0],
        profile_image=profile[1],
        username=username,
        posts=posts
    )

init_db()
