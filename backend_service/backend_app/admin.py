from django.contrib import admin

# Register your models here.


from .models import (
    ActiveAdmin,
    CustomUser,
    Book,
    BorrowRecord,
    FrontendUser
)



class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'email','first_name', 'last_name'
    )
admin.site.register(CustomUser, CustomUserAdmin)


class ActiveAdminAdmin(admin.ModelAdmin):
    list_display = (
        'user','session_id'
    )
admin.site.register(ActiveAdmin, ActiveAdminAdmin)

class FrontendUserAdmin(admin.ModelAdmin):
    list_display = (
        'email','first_name', 'last_name'
    )
admin.site.register(FrontendUser, FrontendUserAdmin)

class BookAdmin(admin.ModelAdmin):
    list_display = (
        'id','title','author', 'category', 'publisher', 'is_available','available_copies'
    )
admin.site.register(Book, BookAdmin)


class BorrowRecordAdmin(admin.ModelAdmin):
    list_display=(
        'id','user_email', 'book','borrow_date','return_date','duration_days'
    )
admin.site.register(BorrowRecord, BorrowRecordAdmin)

