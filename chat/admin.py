from django.contrib import admin
from .models import Conversation, Document, Message

# Registrando a Conversation no admin
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')  # Exibir título, usuário e data de criação na lista
    search_fields = ('title', 'user__username')  # Permitir pesquisa pelo título e nome do usuário
    list_filter = ('created_at',)  # Filtro por data de criação

admin.site.register(Conversation, ConversationAdmin)

# Registrando o Document no admin
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'conversation', 'uploaded_at')  # Exibir nome, conversa e data de upload
    search_fields = ('name', 'conversation__title')  # Permitir pesquisa pelo nome do documento e título da conversa
    list_filter = ('uploaded_at',)  # Filtro por data de upload

admin.site.register(Document, DocumentAdmin)

# Registrando o Message no admin
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'content', 'is_bot', 'timestamp')  # Exibir conversa, conteúdo, se é bot e timestamp
    search_fields = ('conversation__title', 'content')  # Permitir pesquisa pelo título da conversa e conteúdo da mensagem
    list_filter = ('is_bot', 'timestamp')  # Filtro por se é bot e data da mensagem

admin.site.register(Message, MessageAdmin)
