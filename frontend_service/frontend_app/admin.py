from django.contrib import admin

# Register your models here.

from .models import (
    CustomUser,
    ActiveUser,
    Book,
    BorrowedBook
)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'email','first_name', 'last_name'
    )
admin.site.register(CustomUser, CustomUserAdmin)


class ActiveUserAdmin(admin.ModelAdmin):
    list_display = (
        'user','session_id'
    )
admin.site.register(ActiveUser, ActiveUserAdmin)

class BookAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title','author', 'category', 'publisher', 'is_available','available_copies'
    )
admin.site.register(Book, BookAdmin)


class BorrowedBookAdmin(admin.ModelAdmin):
    list_display = (
        'id','user', 'book','borrowed_at', 'duration_days'
    )
admin.site.register(BorrowedBook, BorrowedBookAdmin)
