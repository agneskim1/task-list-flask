from app import db
from flask import Blueprint, make_response, jsonify, abort, request 
from app.models.goal import Goal
from app.routes import validate_model


goals_bp = Blueprint("goal", __name__, url_prefix = "/goals")

@goals_bp.route("", methods = ["POST"])
def post_one_goal():
    request_body = request.get_json()

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
