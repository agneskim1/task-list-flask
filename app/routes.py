from flask import Blueprint, make_response, request, jsonify, abort
from app.models.task import Task
from app import db

tasks_bp = Blueprint("task",__name__, url_prefix = "/tasks")

def validate_id(task_id):
    try:
        task_id = int(task_id)
    except:
        abort(make_response({"details": "Invalid data"}, 400))
    
    task = Task.query.get(task_id)
    if not task:
        abort(make_response({"message": f"Task {task_id} does not exist"}, 404))
    return task

def validate_arguments(request_body, argument):
    try:
        request_body.get(argument)
    except:
        abort(make_response({"details": "Invalid data"}, 400))
    


@tasks_bp.route("", methods = ["POST"])
def post_one_task():
    request_body = request.get_json()
    try:
        request_body["title"]
        request_body["description"]
    except:
        abort(make_response({"details": "Invalid data"}, 400))
    
    if not request_body.get("completed_at"):
        request_body["completed_at"] = None
    
    task = Task(
        title = request_body["title"],
        description = request_body["description"],
        completed_at = request_body["completed_at"]
    )

    db.session.add(task)
    db.session.commit()

    if not task.completed_at:
        task.completed_at = False
    return make_response({"task": {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at
    } }, "201 CREATED")

@tasks_bp.route("", methods = ["GET"])
def get_all_tasks():
    task_response = []
    tasks = Task.query.all()
    
    for task in tasks:
        if not task.completed_at:
            task.completed_at = False
        task_response.append({
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at
        })
    return jsonify(task_response)

@tasks_bp.route("/<task_id>", methods = ["GET"])
def get_one_task(task_id):
    task = validate_id(task_id)
    
    if not task.completed_at:
        task.completed_at = False
    return {"task" : {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at
    }}

@tasks_bp.route("/<task_id>", methods = ["PUT"])
def update_one_task(task_id):

    request_body = request.get_json()

    task = validate_id(task_id)

    if not request_body.get("completed_at"):
        request_body["completed_at"] = None

    task.title = request_body["title"]
    task.description = request_body["description"]
    task.is_complete = request_body["completed_at"]


    db.session.commit()

    if not task.completed_at:
        task.completed_at = False
    return {"task" : {
        "id": task.task_id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at
    }} 

@tasks_bp.route("/<task_id>", methods = ["DELETE"])
def delete_one_task(task_id):
    task = validate_id(task_id)

    db.session.delete(task)
    db.session.commit()

    return {"details": f"Task {task_id} \"Go on my daily walk 🏞\" successfully deleted"}