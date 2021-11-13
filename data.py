from main import BlogPost, db, User

db.create_all()

user = User(
    name="Luis Moreno",
    email="admin@email.com",
    password="pbkdf2:sha256:150000$S6rJcRYW$5185102363836c5d68a72f70c44debf893e8d8b7dc5abb352e9bcab0f3023289"
)
db.session.add(user)

post = BlogPost(
    title="Hello world!: The inlet door to the programming universe",
    subtitle="Programming in the 21st century",
    date="November 11, 2021",
    body="<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>",
    img_url="https://cdn-images-1.medium.com/max/1600/1*U-R58ahr5dtAvtSLGK2wXg.png"
)

db.session.add(post)
db.session.commit()
