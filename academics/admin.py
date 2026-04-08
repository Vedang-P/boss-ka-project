from django.contrib import admin

from .models import Course, GradeComponent, Task


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "user", "connection", "current_grade_percent")
    search_fields = ("title", "code", "user__username")


@admin.register(GradeComponent)
class GradeComponentAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "weight_percent", "override_weight_percent", "source")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "task_type", "course", "due_at", "priority_score", "is_completed")
    list_filter = ("task_type", "difficulty", "is_completed", "source")
    search_fields = ("title", "course__title", "user__username")
