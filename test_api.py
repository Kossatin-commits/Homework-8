import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_create_task():
    print("\n--- Тест: Создание задачи ---")
    url = f"{BASE_URL}/tasks"
    headers = {"Content-Type": "application/json"}
    data = {"title": "Помыть кота", "priority": "low"}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status() # Вызывает исключение для HTTP ошибок 4xx/5xx
        created_task = response.json()
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {json.dumps(created_task, indent=2, ensure_ascii=False)}")
        assert response.status_code == 201
        assert created_task['title'] == data['title']
        assert created_task['priority'] == data['priority']
        assert created_task['isDone'] is False
        assert 'id' in created_task
        print("Создание задачи: УСПЕШНО")
        return created_task['id']
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании задачи: {e}")
        if e.response:
            print(f"Статус: {e.response.status_code}")
            print(f"Ответ: {e.response.text}")
        print("Создание задачи: ПРОВАЛ")
        return None

def test_get_all_tasks():
    print("\n--- Тест: Получение всех задач ---")
    url = f"{BASE_URL}/tasks"

    try:
        response = requests.get(url)
        response.raise_for_status()
        tasks_list = response.json()
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {json.dumps(tasks_list, indent=2, ensure_ascii=False)}")
        assert response.status_code == 200
        assert isinstance(tasks_list, list)
        print("Получение всех задач: УСПЕШНО")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении задач: {e}")
        if e.response:
            print(f"Статус: {e.response.status_code}")
            print(f"Ответ: {e.response.text}")
        print("Получение всех задач: ПРОВАЛ")

def test_complete_task(task_id):
    if task_id is None:
        print("\n--- Тест: Отметка о выполнении задачи (пропущен, нет ID) ---")
        return
    print(f"\n--- Тест: Отметка о выполнении задачи ID: {task_id} ---")
    url = f"{BASE_URL}/tasks/{task_id}/complete"

    try:
        response = requests.post(url)
        response.raise_for_status()
        print(f"Статус: {response.status_code}")
        print(f"Ответ: '{response.text}' (ожидается пусто)")
        assert response.status_code == 200
        print(f"Отметка задачи {task_id} как выполненной: УСПЕШНО")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отметке задачи {task_id} как выполненной: {e}")
        if e.response:
            print(f"Статус: {e.response.status_code}")
            print(f"Ответ: {e.response.text}")
        print(f"Отметка задачи {task_id} как выполненной: ПРОВАЛ")


def test_complete_nonexistent_task():
    print("\n--- Тест: Отметка о выполнении несуществующей задачи (ожидаем 404) ---")
    non_existent_id = 99999
    url = f"{BASE_URL}/tasks/{non_existent_id}/complete"

    try:
        response = requests.post(url)
        assert response.status_code == 404
        error_response = response.json()
        print(f"Статус: {response.status_code}")
        print(f"Ответ: {json.dumps(error_response, indent=2, ensure_ascii=False)}")
        assert "Задача с ID" in error_response['description']
        print("Отметка несуществующей задачи: УСПЕШНО (получен 404)")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка (неожиданная) при отметке несуществующей задачи: {e}")
        print("Отметка несуществующей задачи: ПРОВАЛ")


if __name__ == "__main__":
    # Очищаю tasks.txt для чистого запуска тестов, если нужно
    # if os.path.exists("tasks.txt"):
    #     os.remove("tasks.txt")
    #     print("Удален старый tasks.txt для чистого тестирования.")

    task_id_to_complete = test_create_task()
    test_get_all_tasks()
    test_complete_task(task_id_to_complete)
    test_get_all_tasks()  # Проверяю, что задача теперь isDone=true
    test_complete_nonexistent_task()