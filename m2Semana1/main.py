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

@app.route('/tasks', methods=['GET'])
def get_tasks():
    status = request.args.get('status')
    tasks = read_tasks()
    if status:
        if status not in VALID_STATUS:
            return jsonify({"error": f"Invalid status. Must be one of {VALID_STATUS}"}), 400
        tasks = [t for t in tasks if t['status'] == status]
    return jsonify(tasks), 200

@app.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()

    if not data.get('id'):
        return jsonify({"error": "Task ID is required"}), 400
    if not data.get('title'):
        return jsonify({"error": "Title is required"}), 400
    if not data.get('description'):
        return jsonify({"error": "Description is required"}), 400
    if not data.get('status'):
        return jsonify({"error": "Status is required"}), 400
    if data['status'] not in VALID_STATUS:
        return jsonify({"error": f"Invalid status. Must be one of {VALID_STATUS}"}), 400

    tasks = read_tasks()
    if any(t['id'] == data['id'] for t in tasks):
        return jsonify({"error": "Task with this ID already exists"}), 400

    tasks.append({
        "id": data['id'],
        "title": data['title'],
        "description": data['description'],
        "status": data['status']
    })
    save_tasks(tasks)
    return jsonify({"message": "Task created"}), 201

@app.route('/tasks/<string:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    tasks = read_tasks()
    
    task = next((t for t in tasks if t['id'] == task_id), None)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if 'title' in data:
        task['title'] = data['title'] if data['title'] else task['title']
    if 'description' in data:
        task['description'] = data['description'] if data['description'] else task['description']
    if 'status' in data:
        if data['status'] not in VALID_STATUS:
            return jsonify({"error": f"Invalid status. Must be one of {VALID_STATUS}"}), 400
        task['status'] = data['status']

    save_tasks(tasks)
    return jsonify({"message": "Task updated successfully"}), 200

@app.route('/tasks/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = read_tasks()
    new_tasks = [t for t in tasks if t['id'] != task_id]

    if len(tasks) == len(new_tasks):
        return jsonify({"error": "Task not found"}), 404

    save_tasks(new_tasks)
    return jsonify({"message": "Task deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True)
