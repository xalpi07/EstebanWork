from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

FILE_PATH = 'tasks.json'
VALID_STATUS = ["ToDo", "InProgress", "Completed"]

def read_tasks():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=4, ensure_ascii=False)

def success_response(data=None, message=None, status=200):
    response = {"success": True}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return jsonify(response), status

def error_response(error, status=400):
    return jsonify({"success": False, "error": error}), status

def validate_task_data(data, is_update=False):
    if not isinstance(data, dict):
        return "Invalid data format, must be JSON"

    if not is_update: 
        if "id" not in data:
            return "Task ID is required"
        if "title" not in data or not data["title"].strip():
            return "Title is required"
        if "description" not in data or not data["description"].strip():
            return "Description is required"
        if "status" not in data:
            return "Status is required"
    else:  
        if "title" in data and not data["title"].strip():
            return "Title cannot be empty"
        if "description" in data and not data["description"].strip():
            return "Description cannot be empty"

    if "status" in data and data["status"] not in VALID_STATUS:
        return f"Invalid status. Must be one of {VALID_STATUS}"

    return None

@app.route('/tasks', methods=['GET'])
def get_tasks():
    status = request.args.get('status')
    tasks = read_tasks()
    if status:
        if status not in VALID_STATUS:
            return error_response(f"Invalid status. Must be one of {VALID_STATUS}", 400)
        tasks = [t for t in tasks if t['status'] == status]
    return success_response(data=tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    error = validate_task_data(data)
    if error:
        return error_response(error, 400)
    try:
        tasks = read_tasks()
        if any(t['id'] == data['id'] for t in tasks):
            return error_response("Task with this ID already exists", 400)

        task = {
            "id": data['id'],
            "title": data['title'],
            "description": data['description'],
            "status": data['status']
        }
        tasks.append(task)
        save_tasks(tasks)
        return success_response(data=task, message="Task created", status=201)
    except RuntimeError as e:
        return error_response(str(e), 500)

@app.route('/tasks/<string:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    error = validate_task_data(data, is_update=True)
    if error:
        return error_response(error, 400)

    tasks = read_tasks()
    task = next((t for t in tasks if str(t['id']) == task_id), None)
    if not task:
        return error_response("Task not found", 404)

    if 'title' in data:
        task['title'] = data['title']
    if 'description' in data:
        task['description'] = data['description']
    if 'status' in data:
        task['status'] = data['status']

    save_tasks(tasks)
    return success_response(data=task, message="Task updated successfully")

@app.route('/tasks/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = read_tasks()
    new_tasks = [t for t in tasks if str(t['id']) != task_id]

    if len(tasks) == len(new_tasks):
        return error_response("Task not found", 404)

    save_tasks(new_tasks)
    return success_response(message="Task deleted")

if __name__ == '__main__':
    app.run(debug=True)
