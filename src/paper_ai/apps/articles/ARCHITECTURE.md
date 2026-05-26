# Структура приложения `articles`

Компромисс: **Django models + services + тонкий API**, без дублирования entity/ORM/mapper.

```
articles/
  models.py           # ArticleProject, ArticlePaper, PromtTemplate (+ бизнес-методы)
  validation.py       # правила полей проекта
  generation/         # статусы, шаги LLM-пайплайна, политика переходов
  services/
    project.py        # create / get / delete
    generation.py     # start + run LLM-шага
    finalize.py       # склейка статьи + SEO (без LLM)
    prompts.py        # сборка промпта
    seo.py            # SEO-анализ
  llm/                # клиент OpenAI / fake
  api/                # django-ninja routes
  tasks.py            # Celery → services (не api)
  exceptions/         # доменные ошибки для API
```

## Поток генерации

1. `POST /projects/{id}/start` → `services.generation.start_generation`
2. Celery `tasks.run_generation_step` → `services.generation.run_generation_step`
3. LLM-шаги: title → intro → chapters names → chapters content (N раз)
4. После последней главы: `services.finalize.finalize_article` (склейка + SEO → `completed`)

Промпты: модель `PromtTemplate` в админке Django.
