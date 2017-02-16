from django.contrib import admin
from bridges_api.models import Question, Tag


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title',)

class TagAdmin(admin.ModelAdmin):
    fields = ('name',)
    list_display = ('name',)


admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
