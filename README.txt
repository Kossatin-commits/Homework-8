
Для проверки использовал окно PowerShell, в одном сервер в другом тесты.

Создать задачу
   curl.exe -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\`"title\`": \`"Купить продукты\`", \`"priority\`": \`"high\`"}"

Посмотреть список в браузере
   http://localhost:8000/tasks

Выполнить задачу
   curl.exe -X POST http://localhost:8000/tasks/1/complete