from django.db import models
from django.contrib.auth.models import User
import os

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuário")
    title = models.CharField(max_length=200, verbose_name="Título")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Conversa"
        verbose_name_plural = "Conversas"


class Document(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, verbose_name="Conversa")
    file = models.FileField(upload_to='documents/', verbose_name="Arquivo")
    name = models.CharField(max_length=255, verbose_name="Nome")
    content = models.TextField(verbose_name="Conteúdo")  # Conteúdo extraído armazenado
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Data de upload")

    def delete(self, *args, **kwargs):
        # Exclui o arquivo quando o documento é deletado
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = "Documento"
        verbose_name_plural = "Documentos"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, verbose_name="Conversa")
    content = models.TextField(verbose_name="Conteúdo")
    is_bot = models.BooleanField(default=False, verbose_name="É bot")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Data e hora")

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Mensagem"
        verbose_name_plural = "Mensagens"
