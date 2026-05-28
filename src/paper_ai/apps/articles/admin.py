from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils.html import format_html

from .exceptions.generation_ex import InvalidGenerationStepException
from .exceptions.status_ex import InvalidStatusChangeException
from .models import ArticlePaper, ArticleProject, LLMModels, LlmTokenPrice, PromtTemplate
from .services.generation import save_generation_estimate, start_generation
from .tasks import run_generation_step


@admin.register(ArticlePaper)
class ArticlePaperAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "article_title",
        "created_at",
        "article_introduction",
        "article_chapters_name",
        "article_chapters_contents",
        "final_article",
        "problems",
    ]


@admin.register(LLMModels)
class LLMModelsAdmin(admin.ModelAdmin):
    list_display = ["id", "model_name", "model_system_name"]
    search_fields = ["model_name", "model_system_name"]


@admin.register(LlmTokenPrice)
class LlmTokenPriceAdmin(admin.ModelAdmin):
    list_display = [
        "model_name",
        "input_price",
        "output_price",
        "cached_input_price",
        "per_count_tokens",
    ]
    search_fields = ["model_name"]


@admin.register(ArticleProject)
class ArticleProjectAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "marker",
        "status",
        "llm_model",
        "estimated_cost_total",
        "cost_input",
        "cost_output",
        "cost_total",
        "created_at",
        "count_chapters",
    ]
    fields = [
        "marker",
        "status",
        "llm_model",
        "count_chapters",
        "depth",
        "width",
        "n_gramms",
        "about_author",
        "article_paper",
        "estimated_cost_input",
        "estimated_cost_output",
        "estimated_cost_total",
        "cost_input",
        "cost_output",
        "cost_total",
        "estimate_cost_button",
        "start_generation_button",
        "created_at",
    ]
    readonly_fields = [
        "estimate_cost_button",
        "start_generation_button",
        "estimated_cost_input",
        "estimated_cost_output",
        "estimated_cost_total",
        "cost_input",
        "cost_output",
        "cost_total",
        "created_at",
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/estimate-cost/",
                self.admin_site.admin_view(self.estimate_cost_view),
                name="articles_articleproject_estimate_cost",
            ),
            path(
                "<path:object_id>/start-generation/",
                self.admin_site.admin_view(self.start_generation_view),
                name="articles_articleproject_start_generation",
            ),
        ]
        return custom_urls + urls

    def estimate_cost_button(self, obj: ArticleProject):
        if not obj.pk:
            return "—"
        url = reverse(
            "admin:articles_articleproject_estimate_cost",
            args=[obj.pk],
        )
        return format_html(
            '<a class="button" href="{}">Посчитать смету</a>',
            url,
        )

    estimate_cost_button.short_description = "Смета"

    def start_generation_button(self, obj: ArticleProject):
        if not obj.pk:
            return "—"
        url = reverse(
            "admin:articles_articleproject_start_generation",
            args=[obj.pk],
        )
        return format_html(
            '<a class="button" href="{}">Запустить генерацию</a>',
            url,
        )

    start_generation_button.short_description = "Генерация"

    def estimate_cost_view(self, request, object_id):
        project = self.get_object(request, object_id)
        if project is None:
            self.message_user(request, "Проект не найден.", level=messages.ERROR)
            return HttpResponseRedirect(reverse("admin:articles_articleproject_changelist"))

        if not project.llm_model_id:
            self.message_user(
                request,
                "Выберите LLM-модель, нажмите «Сохранить», затем считайте смету.",
                level=messages.ERROR,
            )
            return HttpResponseRedirect(
                reverse("admin:articles_articleproject_change", args=[object_id])
            )

        try:
            save_generation_estimate(str(project.id))
        except InvalidGenerationStepException as exc:
            self.message_user(request, str(exc), level=messages.ERROR)
        else:
            self.message_user(
                request,
                "Смета пересчитана. Обновите страницу, чтобы увидеть estimated_cost_*.",
                level=messages.SUCCESS,
            )

        return HttpResponseRedirect(
            reverse("admin:articles_articleproject_change", args=[object_id])
        )

    def start_generation_view(self, request, object_id):
        project = self.get_object(request, object_id)
        if project is None:
            self.message_user(request, "Проект не найден.", level=messages.ERROR)
            return HttpResponseRedirect(reverse("admin:articles_articleproject_changelist"))

        if not project.llm_model_id:
            self.message_user(
                request,
                "Выберите LLM-модель, нажмите «Сохранить», затем запускайте генерацию.",
                level=messages.ERROR,
            )
            return HttpResponseRedirect(
                reverse("admin:articles_articleproject_change", args=[object_id])
            )

        try:
            start_generation(str(project.id))
            run_generation_step.delay(str(project.id))
        except (InvalidStatusChangeException, InvalidGenerationStepException) as exc:
            self.message_user(request, str(exc), level=messages.ERROR)
        else:
            self.message_user(
                request,
                "Генерация запущена. Обновите страницу, чтобы увидеть статус и стоимость.",
                level=messages.SUCCESS,
            )

        return HttpResponseRedirect(
            reverse("admin:articles_articleproject_change", args=[object_id])
        )


@admin.register(PromtTemplate)
class PromtTemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "status", "expected_output_ratio", "template"]
