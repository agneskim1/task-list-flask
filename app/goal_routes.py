from app import db
from flask import Blueprint, make_response, jsonify, abort, request 
from app.models.goal import Goal
from app.models.task import Task
from app.routes import validate_model


goals_bp = Blueprint("goal", __name__, url_prefix = "/goals")

@goals_bp.route("", methods = ["POST"])
def post_one_goal():
    request_body = request.get_json()
    try:
        request_body["title"]
    except:
        abort(make_response({"details": "Invalid data"}, 400))
    goal = Goal(
        title = request_body["title"]
    )

    db.session.add(goal)
    db.session.commit()

    return make_response({"goal": {
        "id": goal.goal_id,
        "title": goal.title    
        }},"201 CREATED")

@goals_bp.route("", methods = ["GET"])
def get_all_goals():
    goal_response =[]

    goals = Goal.query.all()

    for goal in goals:
        goal_response.append({
            "id": goal.goal_id,
            "title": goal.title
        })
    return jsonify(goal_response)

@goals_bp.route("/<goal_id>", methods = ["GET"])
def get_one_goal(goal_id):
    goal = validate_model(goal_id, Goal)

    return {"goal" :{
        "id": goal.goal_id,
        "title": goal.title
    }}
@goals_bp.route("/<goal_id>", methods = ["PUT"])
def update_goal_title(goal_id):
    goal = validate_model(goal_id, Goal)

    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit()

    return make_response({"goal": {
        "id": goal.goal_id,
        "title": goal.title
    }})

@goals_bp.route("/<goal_id>", methods = ["DELETE"])
def delete_one_goal(goal_id):
    goal= validate_model(goal_id, Goal)

    db.session.delete(goal)

    db.session.commit()
    return {  "details": f'Goal {goal_id} "{goal.title}" successfully deleted'}

#nested routes with goal and tasks
@goals_bp.route("/<goal_id>/tasks", methods = ["POST"])
def create_new_task_to_specific_goal(goal_id):
    goal=validate_model(goal_id, Goal)

    request_body = request.get_json()
    task_ids = request_body["task_ids"]
    
    for task in task_ids:
        task = validate_model(task, Task)
        if not task.goal_id:
            new_task = Task(
                title = task.title,
                description = task.description,
                completed_at = task.completed_at,
                goal = goal
            )

            db.session.add(new_task)
            db.session.commit()

    return make_response({
        "id": goal.goal_id,
        "task_ids": request_body["task_ids"]
    }, "200 OK")

@goals_bp.route("/<goal_id>/tasks", methods = ["GET"])
def get_all_tasks_from_one_goal_id(goal_id):
    goal=validate_model(goal_id, Goal)
    tasks = Task.query.filter_by(goal_id = goal.goal_id)
    task_list = []

    for task in tasks:
        if not task.completed_at:
            task.completed_at = False
        task_list.append({
            "id": task.task_id,
            "goal_id": task.goal_id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at
        })
    

    return make_response({
        "id": goal.goal_id,
        "title": goal.title,
        "tasks": task_list
    }, "200 OK")
