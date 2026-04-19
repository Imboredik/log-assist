# log-assist

Инфраструктура для сбора, хранения и анализа логов с веб-интерфейсом.

**Мой вклад:** Полностью настроил Docker-оркестрацию всего проекта (7 сервисов).

## Технологии

| Компонент | Технология |
|-----------|------------|
| База данных | PostgreSQL |
| Объектное хранилище | MinIO (S3-совместимое) |
| Бэкенд API | Python (FastAPI) |
| Фронтенд | Vue.js |
| Сбор логов | Fluentd |
| Поиск и аналитика | Elasticsearch |
| Визуализация | Kibana |

## Архитектура
Фронтенд (Vue.js) ──► API (FastAPI) ──┬──► PostgreSQL
│ ├──► MinIO (изображения)
│ └──► OpenRouter AI (анализ)
│
└──► Fluentd ──► Elasticsearch ──► Kibana


## Запуск всего проекта

```bash
# Клонировать репозиторий
git clone https://github.com/Imboredik/log-assist.git
cd log-assist

# Запустить все сервисы
docker-compose -f docker-compose.prod.yml up --build
