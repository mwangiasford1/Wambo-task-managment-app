from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/task_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define the Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f"<Task {self.id}: {self.content}>"

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form.get("task")
        if not task_content.strip():
            flash("Task content cannot be empty!")
            return redirect('/')

        new_task = Todo(content=task_content, completed=False)

        try:
            db.session.add(new_task)
            db.session.commit()
            flash("Task added successfully!")
        except Exception as e:
            flash(f"An error occurred: {e}")

        return redirect('/')
    else:
        todos = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=todos)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task_to_delete = Todo.query.get_or_404(task_id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        flash("Task deleted successfully!")
    except Exception as e:
        flash(f"An error occurred: {e}")

    return redirect('/')

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task_to_update = Todo.query.get_or_404(task_id)
    task_to_update.completed = not task_to_update.completed

    try:
        db.session.commit()
        flash("Task status updated successfully!")
    except Exception as e:
        flash(f"An error occurred: {e}")

    return redirect('/')

@app.route('/test-db')
def test_db():
    try:
        db.session.execute('SELECT 1')
        return "Database connection successful!"
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)
    