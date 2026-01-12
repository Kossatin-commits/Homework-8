import http.server
import json
import os

PORT = 8000
DB_FILE = 'tasks.txt'


class TodoHandler(http.server.BaseHTTPRequestHandler):
    tasks = []
    next_id = 1

    @classmethod
    def load_tasks(cls):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    cls.tasks = json.load(f)
                    if cls.tasks:
                        cls.next_id = max(task['id'] for task in cls.tasks) + 1
            except Exception as e:
                print(f"Ошибка загрузки файла: {e}")

    def save_tasks(self):
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=4)

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        if self.path == '/tasks':
            self._set_headers(200)
            response = json.dumps(self.tasks, ensure_ascii=False)
            self.wfile.write(response.encode('utf-8'))
        else:
            self._set_headers(404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        # 1 СОЗДАНИЕ ЗАДАЧИ
        if self.path == '/tasks':
            try:
                data = json.loads(post_data.decode('utf-8'))
                new_task = {
                    "id": TodoHandler.next_id,
                    "title": data.get("title", "Без названия"),
                    "priority": data.get("priority", "normal"),
                    "isDone": False
                }
                TodoHandler.tasks.append(new_task)
                TodoHandler.next_id += 1
                self.save_tasks()

                self._set_headers(200)
                self.wfile.write(json.dumps(new_task, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self._set_headers(400)

        # 2 ВЫПОЛНЕНИЕ ЗАДАЧИ
        elif self.path.startswith('/tasks/') and self.path.endswith('/complete'):
            try:
                parts = self.path.split('/')
                task_id = int(parts[2])

                task = next((t for t in TodoHandler.tasks if t['id'] == task_id), None)

                if task:
                    task['isDone'] = True
                    self.save_tasks()
                    self._set_headers(200)
                    self.wfile.write(b"")
                else:
                    self._set_headers(404)
            except (IndexError, ValueError):
                self._set_headers(400)
        else:
            self._set_headers(404)


if __name__ == '__main__':
    TodoHandler.load_tasks()
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, TodoHandler)
    print(f"Сервер запущен: http://localhost:{PORT}/tasks")
    httpd.serve_forever()