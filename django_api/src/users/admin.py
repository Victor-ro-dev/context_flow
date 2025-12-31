from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'role', 'is_active', 'created_at')
    list_filter = ('is_active', 'role', 'created_at')
    search_fields = ('email', 'username')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Informações Pessoais', {'fields': ('id', 'email', 'username', 'role')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Data e Hora', {'fields': ('created_at', 'updated_at')}),
    )
