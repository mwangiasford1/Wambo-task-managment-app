from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/task_db'
app.secret_key = "supersecretkey"
db = SQLAlchemy(app)

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
            return redirect('/')
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
        return redirect('/')
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
        return redirect('/')
    except Exception as e:
        flash(f"An error occurred: {e}")
        return redirect('/')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
