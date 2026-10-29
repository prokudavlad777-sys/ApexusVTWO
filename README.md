# APEXUS 1V — AI-чат на PySide6 (DeepSeek)

Темний преміальний десктопний застосунок для Windows. Інтерфейс українською.

## Структура
```
main.py            — точка входу (сама докачує бібліотеки)
interface.py       — інтерфейс PySide6
chat.py            — чати, локальна історія, DeepSeek API
settings.py        — налаштування
requirements.txt   — залежності
run.bat            — запуск подвійним кліком
.github/workflows/build.yml — збірка .exe на GitHub
```

## Запуск (Windows)
1. Встановіть Python 3.12+ з https://www.python.org/downloads/ (галочка **Add python.exe to PATH**).
2. Натисніть «Налаштування» в застосунку, оберіть сервіс (DeepSeek, OpenAI, OpenRouter, Groq, Ollama або власний),
   вставте API-ключ **цього** сервісу й натисніть «Перевірити зʼєднання».
   Ключ можна й задати змінною середовища: `setx DEEPSEEK_API_KEY "ваш_ключ"` (використовується, якщо поле ключа порожнє).
3. Двічі клікніть **run.bat** — при першому запуску бібліотеки завантажаться автоматично.

Або через термінал у папці проєкту:
```
python -m pip install -r requirements.txt
python main.py
```

## Збірка .exe на GitHub
Завантажте файли в репозиторій → вкладка **Actions** → «Збірка APEXUS 1V» → **Run workflow**.
Готовий `APEXUS_1V.exe` буде в **Artifacts** (бібліотеки вже вбудовані).

Історія чатів і налаштування зберігаються в `%APPDATA%\APEXUS_AI`.
