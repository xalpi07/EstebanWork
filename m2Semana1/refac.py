from flask import Flask, request, jsonify
from flask.views import MethodView
import json
import os
import secrets

app = Flask(__name__)

TASKS_FILE = "tasks.json"
TOKENS_FILE = "tokens.json"

VALID_STATUSES = ["ToDo", "InProgress", "Completed"]

USERS = {
    "admin": "password123"
}

def read_json(file_path, default):
    if not os.path.exists(file_path):
        return default
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def read_tasks():
    return read_json(TASKS_FILE, [])

def save_tasks(tasks):
    write_json(TASKS_FILE, tasks)

def read_tokens():
    return read_json(TOKENS_FILE, {})

def save_tokens(tokens):
    write_json(TOKENS_FILE, tokens)

def auth_required(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        tokens = read_tokens()

        if token not in tokens.values():
            return jsonify({"error": "Unauthorized"}), 401

        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if USERS.get(username) != password:
        return jsonify({"error": "Invalid credentials"}), 401
    
    token = secrets.token_hex(16)

    tokens = read_tokens()
    tokens[username] = token
    save_tokens(tokens)

    return jsonify({"token": token}), 200

class TaskAPI(MethodView):
    decorators = [auth_required]

    def get(self, task_id=None):
        tasks = read_tasks()
        status = request.args.get("status")

        if task_id:
            task = next((t for t in tasks if t["id"] == task_id), None)
            if not task:
                return jsonify({"error": "Task not found"}), 404
            return jsonify(task), 200

        if status:
            if status not in VALID_STATUSES:
                return jsonify({"error": f"Invalid status. Must be one of {VALID_STATUSES}"}), 400
            tasks = [t for t in tasks if t["status"] == status]

        return jsonify(tasks), 200

    def post(self):
        data = request.get_json()
        if not data.get("id"):
            return jsonify({"error": "Task ID is required"}), 400
        if not data.get("title"):
            return jsonify({"error": "Title is required"}), 400
        if not data.get("description"):
            return jsonify({"error": "Description is required"}), 400
        if not data.get("status"):
            return jsonify({"error": "Status is required"}), 400
        if data["status"] not in VALID_STATUSES:
            return jsonify({"error": f"Invalid status. Must be one of {VALID_STATUSES}"}), 400

        tasks = read_tasks()
        if any(t["id"] == data["id"] for t in tasks):
            return jsonify({"error": "Task with this ID already exists"}), 400

        tasks.append(data)
        save_tasks(tasks)
        return jsonify({"message": "Task created successfully"}), 201

    def put(self, task_id):
        tasks = read_tasks()
        task = next((t for t in tasks if t["id"] == task_id), None)
        if not task:
            return jsonify({"error": "Task not found"}), 404

        data = request.get_json()
        if "title" in data:
            task["title"] = data["title"]
        if "description" in data:
            task["description"] = data["description"]
        if "status" in data:
            if data["status"] not in VALID_STATUSES:
                return jsonify({"error": f"Invalid status. Must be one of {VALID_STATUSES}"}), 400
            task["status"] = data["status"]

        save_tasks(tasks)
        return jsonify({"message": "Task updated successfully"}), 200

    def delete(self, task_id):
        tasks = read_tasks()
        new_tasks = [t for t in tasks if t["id"] != task_id]
        if len(tasks) == len(new_tasks):
            return jsonify({"error": "Task not found"}), 404

        save_tasks(new_tasks)
        return jsonify({"message": "Task deleted successfully"}), 200

task_view = TaskAPI.as_view("task_api")
app.add_url_rule("/tasks", defaults={"task_id": None}, view_func=task_view, methods=["GET"])
app.add_url_rule("/tasks", view_func=task_view, methods=["POST"])
app.add_url_rule("/tasks/<string:task_id>", view_func=task_view, methods=["GET", "PUT", "DELETE"])

if __name__ == "__main__":
    app.run(debug=True)
