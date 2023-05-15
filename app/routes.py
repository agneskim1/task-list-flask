from flask import Blueprint, make_response, request, jsonify, abort
from app.models.task import Task
from app import db
from sqlalchemy import desc, asc
from datetime import datetime
import requests
import os 

tasks_bp = Blueprint("task",__name__, url_prefix = "/tasks")


def validate_model(model_id,cls):
    try:
        model_id = int(model_id)
    except:
        abort(make_response({"details": "Invalid data"}, 400))
    
    model = cls.query.get(model_id)
    if not model:
        abort(make_response({"message": f"{cls.__name__ } {model_id} does not exist"}, 404))
    return model

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

    return make_response({"task": task.to_dict()}, "201 CREATED")
        

@tasks_bp.route("", methods = ["GET"])
def get_all_tasks():
    
    tasks = Task.query.all()
    
    task_response = [task.to_dict() for task in tasks]
    
    sort_query = request.args.get("sort")
    if sort_query =="desc":
        task_response = sorted(task_response, key = lambda task: task["title"], reverse = True)
    elif sort_query =="asc":
        task_response = sorted(task_response, key = lambda task: task["title"])

    return jsonify(task_response)

@tasks_bp.route("/<task_id>", methods = ["GET"])
def get_one_task(task_id):
    task = validate_model(task_id, Task)
    
    return {"task": task.to_dict()}

@tasks_bp.route("/<task_id>", methods = ["PUT"])
def update_one_task(task_id):

    request_body = request.get_json()

    task = validate_model(task_id, Task)

    if not request_body.get("completed_at"):
        request_body["completed_at"] = None

    task.title = request_body["title"]
    task.description = request_body["description"]
    task.is_complete = request_body["completed_at"]


    db.session.commit()

    return {"task" : task.to_dict()} 

@tasks_bp.route("/<task_id>", methods = ["DELETE"])
def delete_one_task(task_id):
    task = validate_model(task_id, Task)

    db.session.delete(task)
    db.session.commit()

    return {"details": f'Task {task_id} \"{task.title}" successfully deleted'}

@tasks_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def update_mark_to_complete(task_id):
    task = validate_model(task_id, Task)

    task.completed_at = datetime.now()
    db.session.commit()
    
    path = "https://slack.com/api/chat.postMessage"
    key = os.environ.get("SLACK_API_KEY")
    params = {
        "channel": "task-list-project",
        "text": f"Someone just completed the task {task.title}"
    }
    headers = {
        "Authorization": key
    }

    requests.post(url = path, params = params, headers = headers)

    return {"task" : task.to_dict()} 

@tasks_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"])
def update_mark_to_incomplete(task_id):
    task = validate_model(task_id, Task)

    task.completed_at = None
    db.session.commit()

    return {"task" : task.to_dict()} 