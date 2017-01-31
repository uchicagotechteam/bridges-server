from django.contrib import admin
from bridges_api.models import Question


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title',)

admin.site.register(Question, QuestionAdmin)
