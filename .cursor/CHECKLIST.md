# Чеклист: довести paper_ai до зрелого состояния (2–3 дня)

Цель: один рабочий сценарий end-to-end + тесты + понятный запуск.

**Формула run-step:** не фиксированные «6 шагов», а  
`4 + count_chapters` вызовов LLM (title, intro, names, **N × content**, merge, seo).

---

## Сделано недавно (domain / пайплайн)

- [x] Хук `advance` в `GenerationStep` — переход статуса вынесен из `apply_generation_step`
- [x] Поочерёдная генерация содержимого глав (`add_article_chapters_content`, цикл на `GENERATE_CHAPTERS_CONTENT`)
- [x] `get_count_chapters_content()` — безопасный подсчёт глав без исключений
- [x] Порядок в `apply_generation_step`: `apply → post_apply → advance`

  > Проверено симуляцией в domain: при `count_chapters=3` три run-step на content → `MERGE_ARTICLE`.

- [x] `PromtBuilder`: плейсхолдер номера текущей главы (`chapter_index` / `chapter_number`) для промпта «напиши главу N»
- [ ] Явная проверка `get_next_status()` на `None` в `_advance_to_next_step` (сейчас TODO в коде)

---

## День 1 — «Чтобы проект вообще завёлся»

### Django и база

- [x] Подключить app в `INSTALLED_APPS` (`paper_ai.apps.articles`, поправить `apps.py`)
- [x] Импортировать ORM-модели в `models.py` (чтобы Django их увидел)
- [x] Запустить `makemigrations` и `migrate` без ошибок

  > Миграций в репозитории пока нет — первый `makemigrations` обязателен.

- [x] Зарегистрировать модели в `admin.py` (проект, статья, шаблоны промптов)

- [x] Добавить поле `problems` в `ArticlePaperORM` (JSONField)
- [x] Пробросить `problems` в `article_paper_mapper.py` (to_domain / to_orm)

- [ ] Проверить `ArticleProjectORMRepository.save()` — обновление существующей записи, а не только insert

  > `save()` вызывает `paper_orm.save()` + `article_project_orm.save()` с тем же `id` — в Django это UPDATE. Нужен ручной прогон: create → два `run-step` подряд → в admin одна запись, без дубликатов FK.

- [x] Убрать циклический import между `article_project.py` и `article_paper.py` в ORM (если есть)

### Быстрые правки domain

- [ ] Убрать или не использовать лишние статусы: `NOT_STARTED`, `STARTED` (оставить один путь: `NEW → GENERATE_TITLE`)

  > Статусы всё ещё в `ProjectStatus` и `status_transition_policy`. `STARTED` в `in_progress_statuses`.

- [x] Исправить mutable default в `ArticlePaper`: `problems: list[str] = []` → `problems: list[str] | None = None`

  > В `__init__` по-прежнему `problems=[]` — общий список на все экземпляры.

---

## День 2 — «Чтобы было доказательство, что работает»

### Fake LLM и пайплайн

- [ ] Переделать `FakeLLMClient` — разный ответ по статусу / маркеру в промпте

  > Сейчас всегда `'fake response'`. Нужно: `str` для title/intro/content, `list[str]` для names, учёт `count_chapters` для цикла глав.

- [x] Добавить обработку ошибок в `RunStepGenerationUseCase` → перевод в `ERROR` + save

- [ ] Проверить полный ручной сценарий: create → start → run-step × `(4 + count_chapters)` → `COMPLETED`

  > Пример: `count_chapters=3` → **7** вызовов run-step (3 из них — content на одном статусе).

### Тесты (минимум для junior+)

- [ ] Unit: `ArticleProject.start_generation()` — переход `NEW → GENERATE_TITLE`
- [ ] Unit: `apply_generation_step()` — title записывается, статус меняется
- [ ] Unit: поочерёдные главы — `count_chapters=3`, три вызова на `GENERATE_CHAPTERS_CONTENT` → `MERGE_ARTICLE`
- [ ] Unit: `change_status()` — запрет недопустимого перехода
- [ ] Unit: `ArticleSeoAnalyzer` — находит проблему с depth/width
- [ ] Unit: `PromtBuilder` — подставляет `{marker}`, пустые поля статьи → `''`
- [ ] Integration: Django TestCase — create → start → полный пайплайн с `FakeLLMClient` → `COMPLETED`

  > `tests.py` пустой — тестов пока нет.

### Seed данных

- [ ] Создать шаблоны промптов в admin (или fixture) для каждого шага: `generate_title` … `seo_fix`

  > Для content-шага один шаблон на статус `generate_chapters_content` (вызывается N раз).

---

## День 3 — «Чтобы проект выглядел законченным»

### API или точка входа

- [ ] Подключить Django Ninja в `urls.py` (зависимость в `pyproject.toml` уже есть)
- [ ] Эндпоинты: `POST /projects`, `POST /projects/{id}/start`, `POST /projects/{id}/run-step`, `GET /projects/{id}`

- [ ] Простая фабрика/DI: собрать use case с реальными репозиториями и `FakeLLMClient` / `OpenAILLMClient`

### Celery (опционально)

- [ ] Настроить `CELERY_BROKER_URL` в settings
- [ ] Task: `run_generation_step(project_id)` — вызывает use case, пока не `COMPLETED` — ставит себя снова

  > Для глав с `count_chapters > 1` цикл должен крутиться на `GENERATE_CHAPTERS_CONTENT`, пока `advance` не переведёт на merge.

### Документация и гигиена

- [ ] Написать `README.md`: что делает проект, как установить, как прогнать генерацию
- [ ] Добавить `.env.example` с `OPENAI_API_KEY`
- [ ] Переименовать `application` → `application` (или зафиксировать в README как tech debt)
- [ ] Перенести ABC репозиториев из `adapters/` в `ports/`
- [ ] Убрать неиспользуемый import `ArticleProject` из `LLMClientPort`

---

## Финальная проверка (перед «готово»)

- [ ] `python manage.py test` — все тесты зелёные
- [ ] `migrate` на чистой БД — без ошибок
- [ ] Один проект проходит весь пайплайн до `COMPLETED` (с учётом `count_chapters`)
- [ ] В admin видны: проект, статья, title, chapters, final_article, problems
- [ ] README позволяет повторить это за 10 минут без подсказок

---

## Критерий «зрелый проект»

| Было | Стало |
|------|-------|
| Архитектура без запуска | `migrate` + admin/API работают |
| Логика без доказательств | ≥ 6 тестов, 1 integration |
| Конвейер «на бумаге» | create → start → `4+N` steps → COMPLETED |
| Непонятно как запустить | README + .env.example |
| Главы одним вызовом LLM | По одной главе за run-step (`advance` + append) |

---

## Справка: статусы и шаги генерации

| Статус | LLM-вызовов | Ответ LLM | После шага |
|--------|-------------|-----------|------------|
| `generate_title` | 1 | `str` | → introduction |
| `generate_introduction` | 1 | `str` | → chapters_name |
| `generate_chapters_name` | 1 | `list[str]` (все названия) | → chapters_content |
| `generate_chapters_content` | **count_chapters** | `str` (одна глава) | остаёмся / → merge |
| `merge_article` | 1 | `str` | → seo_fix (+ `find_problems`) |
| `seo_fix` | 1 | `str` | → completed |

---

*Ориентир: 2 дня — MVP (Django + тесты + ручной прогон), 3-й день — API + README + полировка.*
