from django.contrib import admin

from documents.models import Document, DocumentChunk


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_email', 'organization_name', 'status', 'scope', 'created_at')
    list_filter = ('status', 'scope', 'created_at')
    search_fields = ('title', 'user__email', 'organization__name')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    fieldsets = (
        ('Informações Básicas', {'fields': ('id', 'title', 'user', 'organization', 'scope')}),
        ('Arquivo', {'fields': ('file_key', 'file_url', 'mime_type')}),
        ('Status', {'fields': ('status', 'metadata')}),
        ('Data e Hora', {'fields': ('created_at', 'updated_at')}),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else '-'
    user_email.short_description = 'Usuário'

    def organization_name(self, obj):
        return obj.organization.name if obj.organization else '-'
    organization_name.short_description = 'Organização'


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ('document_title', 'chunk_index', 'text_preview')
    list_filter = ('document', 'metadata')
    search_fields = ('text', 'document__title')
    ordering = ('document', 'chunk_index')
    readonly_fields = ('id', 'text_preview')
    fieldsets = (
        ('Informações', {'fields': ('id', 'document', 'chunk_index')}),
        ('Conteúdo', {'fields': ('text', 'embedding')}),
        ('Metadados', {'fields': ('metadata',)}),
    )

    def document_title(self, obj):
        return obj.document.title
    document_title.short_description = 'Documento'

    def text_preview(self, obj):
        return obj.text[:100] + '...' if len(obj.text) > 100 else obj.text
    text_preview.short_description = 'Prévia do Texto'
