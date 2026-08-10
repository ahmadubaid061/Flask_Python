from flask import Blueprint, render_template, redirect, url_for, flash,request, session
from app.models import Task, User
from app import db
tasks = Blueprint('tasks', __name__)    


#---------------------------------------view all tasks---------------------------------------
@tasks.route('/', methods=['GET', 'POST'])
def view_tasks():
    if 'user_id' not in session:
        flash('Please log in to view your tasks.', 'danger')
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    tasks = Task.query.filter_by(user_id=user.id).all()
    return render_template('tasks.html', tasks=tasks, user=user)



#---------------------------------------add task---------------------------------------
@tasks.route('/add', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        flash('Please log in to add tasks.', 'danger')
        return redirect(url_for('auth.login'))
    
    title = request.form.get('title')
    user_id = session['user_id']
    new_task = Task(title=title, user_id=user_id)
    db.session.add(new_task)
    db.session.commit()
    flash('Task added successfully!', 'success')
    return redirect(url_for('tasks.view_tasks'))



#---------------------------------------toggle task status---------------------------------------
@tasks.route('/toggle/<int:task_id>', methods=['POST'])
def toggle_task(task_id):
    if 'user_id' not in session:
        flash('Please log in to update tasks.', 'danger')
        return redirect(url_for('auth.login'))
    
    task = Task.query.get(task_id)
    if task:
        if task.status == 'Pending':
            task.status = 'inProcess'
        elif task.status == 'inProcess':
            task.status = 'Completed'
        else:
            task.status = 'Pending'
        db.session.commit()
        flash('Task status updated successfully!', 'success')
    else:
        flash('Task not found.', 'danger')
    return redirect(url_for('tasks.view_tasks'))


#---------------------------------------delete task---------------------------------------
@tasks.route('/delete/<int:task_id>', methods=['POST']) 
def delete_task(task_id):
    if 'user_id' not in session:
        flash('Please log in to delete tasks.', 'danger')
        return redirect(url_for('auth.login'))
    
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    else:
        flash('Task not found.', 'danger')
    return redirect(url_for('tasks.view_tasks'))