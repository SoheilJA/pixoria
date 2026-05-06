from django.contrib import admin
from .models import HomePage

@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ['main_title', 'second_title', 'text_preview']

    @admin.display(description='متن')
    def text_preview(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    def has_add_permission(self, request):
        # اگر رکورد وجود دارد، دکمه Add را مخفی کن
        return not HomePage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # اجازه حذف نده
        return False
