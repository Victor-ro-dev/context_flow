import uuid
from typing import TypedDict

from django.conf import settings
from django.db import models

# Create your models here.

class ChunkMetadata(TypedDict, total=False):
        """Metadados do chunk."""
        page_number: int
        section: str
        confidence_score: float
        char_start: int
        char_end: int

class DocumentMetadata(TypedDict, total=False):
        """Metadados do documento."""
        pages: int
        language: str
        keywords: list[str]
        custom_field: str

class Document(models.Model):
    """
    Modelo para armazenar documentos carregados pelos usuários.
    """
    class ScopeChoices(models.TextChoices):
        USER = "USER", "Usuário"
        ORGANIZATION = "ORGANIZATION", "Organização"
    SCOPE_CHOICES = [
        (ScopeChoices.USER, "USER"),
        (ScopeChoices.ORGANIZATION, "ORGANIZATION"),
        ]

    class StatusChoices(models.TextChoices):
        UPLOADED = "UPLOADED", "Carregado"
        PROCESSING = "PROCESSING", "Processando"
        INDEXED = "INDEXED", "Indexado"
        FAILED = "FAILED", "Falhou"

    STATUS_CHOICES = [
        (StatusChoices.UPLOADED, "UPLOADED"),
        (StatusChoices.PROCESSING, "PROCESSING"),
        (StatusChoices.INDEXED, "INDEXED"),
        (StatusChoices.FAILED, "FAILED"),
        ]


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents', help_text="Usuário que carregou o documento.")
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='documents', null=True, blank=True, help_text="Organização associada ao documento, se aplicável.")
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default=ScopeChoices.USER, help_text="Escopo do documento: usuário ou organização.")
    title = models.CharField(max_length=255, help_text="Título do documento.")
    file_key = models.FileField(upload_to='documents/', help_text="Chave no MinIO onde o documento está armazenado.")
    file_url = models.URLField(max_length=2048, blank=True, help_text="URL acessível publicamente para o documento armazenado.")
    mime_type = models.CharField(max_length=100, help_text="Tipo MIME do documento.", default="application/pdf")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=StatusChoices.UPLOADED, help_text="Status atual do documento no fluxo de processamento.")
    metadata = models.JSONField(blank=True, default=dict, help_text="Metadados adicionais relacionados ao documento.") # type: ignore
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'documents'
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f"{self.title}"

class DocumentChunk(models.Model):
    """
    Chunks de texto extraído dos documentos, com em embeddings para busca.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks', help_text="Documento ao qual este chunk pertence.")
    chunk_index = models.IntegerField(help_text="Índice do chunk dentro do documento.")
    text = models.TextField(help_text="Texto extraído deste chunk do documento.")
    embedding = models.TextField(blank=True, help_text='Será vector(1536) com pgvector')
    metadata= models.JSONField(blank=True, default=dict, help_text="Metadados adicionais relacionados ao chunk.") # type: ignore

    class Meta:
        db_table = 'document_chunks'
        verbose_name = 'Chunk de Documento'
        verbose_name_plural = 'Chunks de Documentos'
        unique_together = ('document', 'chunk_index')
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]
    def __str__(self) -> str:
        return f"Chunk {self.chunk_index} of Document {self.document.title}"
