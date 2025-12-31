from django.contrib import admin

from queries.models import AuditLog, QueryLog


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'organization_name', 'query_preview', 'latency_ms', 'tokens_used', 'created_at')
    list_filter = ('created_at', 'latency_ms')
    search_fields = ('user__email', 'organization__name', 'query_text')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Informações Básicas', {'fields': ('id', 'user', 'organization')}),
        ('Conteúdo', {'fields': ('query_text', 'answer_text')}),
        ('Métricas', {'fields': ('latency_ms', 'tokens_used', 'citations')}),
        ('Data e Hora', {'fields': ('created_at',)}),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'Usuário'

    def organization_name(self, obj):
        return obj.organization.name if obj.organization else '-'
    organization_name.short_description = 'Organização'

    def query_preview(self, obj):
        return obj.query_text[:50] + '...' if len(obj.query_text) > 50 else obj.query_text
    query_preview.short_description = 'Query'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'organization_display', 'action', 'resource_type', 'ip_address', 'created_at')
    list_filter = ('action', 'resource_type', 'created_at')
    search_fields = ('user__email', 'organization__name', 'action')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Informações Básicas', {'fields': ('id', 'user', 'organization', 'action')}),
        ('Recurso', {'fields': ('resource_type', 'resource_id')}),
        ('Rede', {'fields': ('ip_address',)}),
        ('Data e Hora', {'fields': ('created_at',)}),
    )

    def user_display(self, obj):
        return obj.user.email if obj.user else 'Sistema'
    user_display.short_description = 'Usuário'

    def organization_display(self, obj):
        return obj.organization.name if obj.organization else '-'
    organization_display.short_description = 'Organização'
