from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from bridges_api.models import (
    Question, Tag, UserProfile, Employer, DataFile, Position, Ethnicity, Gender
)

class CustomUserAdmin(UserAdmin):
    def response_add(self, request, obj, post_url_continue=None):
        """This makes the response go to the newly created model's change page
        without using reverse"""
        return HttpResponseRedirect("../../../bridges_api/userprofile/%s/change/" % obj.id)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title',)

class TagAdmin(admin.ModelAdmin):
    fields = ('attribute','value')
    list_display = ('value',)

class EmployerAdmin(admin.ModelAdmin):
	list_display = ('name',)

class DataFileAdmin(admin.ModelAdmin):
    list_display = ('name', )

class ParticipantAttributeAdmin(admin.ModelAdmin):
    fields = ('name', 'average_salary', 'num_participants')
    list_display = ('name', )

class PositionAdmin(ParticipantAttributeAdmin):
    pass

class EthnicityAdmin(ParticipantAttributeAdmin):
    pass

class GenderAdmin(ParticipantAttributeAdmin):
    pass

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Employer, EmployerAdmin)
admin.site.register(DataFile, DataFileAdmin)
admin.site.register(Position, PositionAdmin)
admin.site.register(Ethnicity, EthnicityAdmin)
admin.site.register(Gender, GenderAdmin)
