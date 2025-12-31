from django.contrib import admin

from organizations.models import Organization, OrganizationMember


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'members_count')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'slug')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Informações', {'fields': ('id', 'name', 'slug')}),
        ('Data e Hora', {'fields': ('created_at', 'updated_at')}),
    )

    def members_count(self, obj):
        return obj.members.count()
    members_count.short_description = 'Quantidade de Membros'


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'organization_name', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__email', 'organization__name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Informações', {'fields': ('id', 'organization', 'user', 'role')}),
        ('Data e Hora', {'fields': ('created_at',)}),
    )

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email do Usuário'

    def organization_name(self, obj):
        return obj.organization.name
    organization_name.short_description = 'Organização'
