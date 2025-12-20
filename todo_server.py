from flask import Flask, request, jsonify, abort
import json
import os

app = Flask(__name__)

TASKS_FILE = "tasks.txt"

tasks = []
next_task_id = 1


def load_tasks_from_file():
    global tasks, next_task_id
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, 'r', encoding='utf-8') as f:
                loaded_tasks = json.load(f)
                tasks.extend(loaded_tasks)
                print(f"Загружено {len(tasks)} задач из {TASKS_FILE}")

            if tasks:
                next_task_id = max(task['id'] for task in tasks) + 1
            else:
                next_task_id = 1
            print(f"Следующий ID для задачи: {next_task_id}")
        except json.JSONDecodeError:
            print(f"Предупреждение: Файл {TASKS_FILE} поврежден или пуст, начинаем с чистого списка.")
            tasks = []
            next_task_id = 1
        except Exception as e:
            print(f"Ошибка при загрузке задач из {TASKS_FILE}: {e}")
            tasks = []
            next_task_id = 1
    else:
        print(f"Файл {TASKS_FILE} не найден, начинаем с чистого списка.")


def save_tasks_to_file():
    """Сохраняет текущий список задач в файл tasks.txt."""
    try:
        with open(TASKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
        print(f"Задачи успешно сохранены в {TASKS_FILE}")
    except IOError as e:
        print(f"Ошибка при сохранении задач в {TASKS_FILE}: {e}")


# --- API ---

@app.route("/tasks", methods=["POST"])
def create_task():

    global next_task_id
    if not request.is_json:
        abort(400, description="Необходимо отправить JSON-данные.")

    data = request.get_json()
    title = data.get("title")
    priority = data.get("priority")

    if not title or not priority:
        abort(400, description="Поля 'title' и 'priority' обязательны.")

    if priority.lower() not in ["low", "normal", "high"]:
        abort(400, description="Приоритет должен быть 'low', 'normal' или 'high'.")

    new_task = {
        "id": next_task_id,
        "title": title,
        "priority": priority.lower(),
        "isDone": False,
    }
    tasks.append(new_task)
    next_task_id += 1

    save_tasks_to_file()  # Сохраняем после изменения
    return jsonify(new_task), 201  # 201 Created


@app.route("/tasks", methods=["GET"])
def get_all_tasks():
    return jsonify(tasks)


@app.route("/tasks/<int:task_id>/complete", methods=["POST"])
def complete_task(task_id):
    task_found = False
    for task in tasks:
        if task["id"] == task_id:
            task["isDone"] = True
            task_found = True
            break

    if task_found:
        save_tasks_to_file()
        return "", 200  # 200 OK с пустым телом
    else:
        abort(404, description=f"Задача с ID {task_id} не найдена.")


# --- Запуск сервера ---
if __name__ == "__main__":
    load_tasks_from_file()
    app.run(debug=True)