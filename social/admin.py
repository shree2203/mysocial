from django.contrib import admin
from .models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "dob", "gender", "location", "temp_col"]
    readonly_fields = ["gender", "dob", "temp_col"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def get_str(self, obj):
        return obj.temp_col()

    get_str.short_description = 'temp string'


admin.site.register(UserProfile, UserProfileAdmin)
