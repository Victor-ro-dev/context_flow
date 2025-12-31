from django.contrib import admin

from plans.models import Plan, Subscription, Usage


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier', 'plan_type', 'price_monthly', 'max_documents', 'max_storage_mb')
    list_filter = ('tier', 'plan_type', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('tier', 'price_monthly')
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Informações Básicas', {'fields': ('id', 'name', 'tier', 'plan_type')}),
        ('Limites', {'fields': ('max_documents', 'max_storage_mb', 'max_queries', 'max_members')}),
        ('Preço e Descrição', {'fields': ('price_monthly', 'description')}),
        ('Data e Hora', {'fields': ('created_at',)}),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'organization_display', 'plan', 'status', 'created_at')
    list_filter = ('status', 'plan', 'created_at')
    search_fields = ('user__email', 'organization__name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'current_period_start')
    fieldsets = (
        ('Informações', {'fields': ('id', 'user', 'organization', 'plan', 'status')}),
        ('Período', {'fields': ('current_period_start', 'current_period_end')}),
        ('Data e Hora', {'fields': ('created_at',)}),
    )

    def user_display(self, obj):
        return obj.user.email if obj.user else '-'
    user_display.short_description = 'Usuário'

    def organization_display(self, obj):
        return obj.organization.name if obj.organization else '-'
    organization_display.short_description = 'Organização'


@admin.register(Usage)
class UsageAdmin(admin.ModelAdmin):
    list_display = ('user_display', 'organization_display', 'period', 'documents_uploaded', 'queries_executed', 'storage_used_mb')
    list_filter = ('period', 'updated_at')
    search_fields = ('user__email', 'organization__name')
    ordering = ('-period',)
    readonly_fields = ('id', 'updated_at')
    fieldsets = (
        ('Informações', {'fields': ('id', 'user', 'organization', 'period')}),
        ('Uso', {'fields': ('documents_uploaded', 'queries_executed', 'storage_used_mb', 'tokens_used')}),
        ('Data', {'fields': ('updated_at',)}),
    )

    def user_display(self, obj):
        return obj.user.email if obj.user else '-'
    user_display.short_description = 'Usuário'

    def organization_display(self, obj):
        return obj.organization.name if obj.organization else '-'
    organization_display.short_description = 'Organização'
