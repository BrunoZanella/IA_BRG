import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Conversation, Message, Document
from groq import Groq
from django.conf import settings
from .utils.document_processor import DocumentProcessor, create_chunks
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from dotenv import load_dotenv

load_dotenv()  # Carrega variáveis do .env

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('chat_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Você foi desconectado.')
    return redirect('login')

def generate_title(first_message):
    """Gera um título com base na primeira mensagem"""
    title = first_message[:50]
    return title + "..." if len(first_message) > 50 else title

@login_required
def chat_list(request):
    conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chat/chat_list.html', {'conversations': conversations})

@login_required
def new_chat(request):
    conversation = Conversation.objects.create(
        user=request.user,
        title="Novo Chat"
    )
    return redirect('chat_detail', pk=conversation.pk)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import time
from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def search_with_chrome(query):
    """
    Realiza uma busca no Google usando Selenium e retorna os primeiros resultados em HTML.
    """
    # Configuração do ChromeDriver
    options = Options()
    options.add_argument('--headless')  # Executar em modo invisível (headless)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Inicializar o ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Acessar o Google
        driver.get('https://www.google.com')

        # Localizar o campo de busca
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'q'))
        )
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        # Aguardar o carregamento dos resultados
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.tF2Cxc'))
        )

        # Capturar os primeiros resultados
        search_results = driver.find_elements(By.CSS_SELECTOR, 'div.tF2Cxc')
        results = []

        for result in search_results[:3]:  # Limitar a 3 resultados
            # Título
            title = result.find_element(By.CSS_SELECTOR, 'h3').text

            # Link
            link = result.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

            # Snippet (com tratamento para casos ausentes)
            try:
                snippet = result.find_element(By.CSS_SELECTOR, '.VwiC3b').text
            except:
                snippet = "Sem resumo disponível."

            # Formatar como HTML
            results.append(
                f"<strong>{title}</strong><br>"
                f"{snippet}<br>"
                f'<a href="{link}" target="_blank">Acesse o link</a>'
            )

        return "<br><br>".join(results) if results else "Nenhum resultado encontrado."

    except Exception as e:
        return f"Erro ao realizar busca no Google: {str(e)}"
    finally:
        # Fechar o driver
        driver.quit()



@login_required
def chat_detail(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    documents = Document.objects.filter(conversation=conversation)
    
    if request.method == 'POST':
        if 'message' in request.POST:
            user_message = request.POST.get('message')
            if user_message:
                Message.objects.create(
                    conversation=conversation,
                    content=user_message,
                    is_bot=False
                )
                
                if conversation.message_set.count() == 1:
                    conversation.title = generate_title(user_message)
                    conversation.save()
                
                # Preparar contexto dos documentos, se existirem
                document_context = ""
                if documents.exists():
                    document_context = "Use as informações abaixo como referência para as respostas:\n"
                    for doc in documents:
                        document_context += f"- Conteúdo de {doc.name}:\n{doc.content}\n"
                
                # Histórico da conversa
                history = [
                    {
                        "role": "system", 
                        "content": "Voce e um assistente da BRG Geradores."
                                   f"Você está falando com {request.user.username}. "
                                   f"Responda sempre em português de forma educada, clara e direta. "
                                   f"Se houver contexto dos documentos, utilize-o para responder, mas também responda "
                                   f"perguntas fora do contexto dos documentos. Aqui está o contexto:\n{document_context}"
                                   "Sempre envie em formato HTML, colocando textos em destaque em negrito, textos de alerta em vermelho, textos de ok em verde, pule linhas quando mudar alguma informação"
                                   "Não use Markdown"
                                   "Se nao souber a resposta diga, não sei ou não tenho certeza"
                    }
                ]
                
                for msg in conversation.message_set.all():
                    role = "assistant" if msg.is_bot else "user"
                    history.append({"role": role, "content": msg.content})

                '''
                try:
                    chat_completion = client.chat.completions.create(
                        messages=history,
                        model="llama3-8b-8192",
                    )
                    bot_response = chat_completion.choices[0].message.content
                    
                    Message.objects.create(
                        conversation=conversation,
                        content=bot_response,
                        is_bot=True
                    )
                except Exception as e:
                    messages.error(request, "Falha ao obter resposta da IA")
                '''
                                    
                try:
                    chat_completion = client.chat.completions.create(
                        messages=history,
                        model="llama3-8b-8192",
                    )
                    bot_response = chat_completion.choices[0].message.content

                    # Verificar se a IA não sabe a resposta
                    if "não sei" in bot_response.lower() or "não tenho certeza" or "Não soube" in bot_response.lower():
                        bot_response += "<br><br>Buscando informações na internet...<br>"
                        chrome_results = search_with_chrome(user_message)
                        bot_response += chrome_results

                    Message.objects.create(
                        conversation=conversation,
                        content=bot_response,
                        is_bot=True
                    )
                except Exception as e:
                    messages.error(request, "Falha ao obter resposta da IA")
        
        elif 'document' in request.FILES:
            document = request.FILES['document']
            try:
                # Salvar o arquivo temporariamente
                file_path = default_storage.save(f'tmp/{document.name}', ContentFile(document.read()))
                full_path = os.path.join(settings.MEDIA_ROOT, file_path)
                
                # Processar o documento
                processor = DocumentProcessor()
                content = processor.process_document(full_path)
                
                # Criar registro do documento
                Document.objects.create(
                    conversation=conversation,
                    file=file_path,
                    name=document.name,
                    content=content
                )
                
                messages.success(request, f"Documento {document.name} enviado e processado com sucesso!")
            except Exception as e:
                messages.error(request, f"Erro ao processar documento: {str(e)}")
            finally:
                # Limpar arquivo temporário
                if os.path.exists(full_path):
                    os.remove(full_path)
                
    chat_messages = conversation.message_set.all()
    return render(request, 'chat/chat_detail.html', {
        'conversation': conversation,
        'messages': chat_messages,
        'documents': documents,
        'is_chat_detail': True  # Variável de identificação
    })


@login_required
def delete_chat(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    if request.method == 'POST':
        # Isso também excluirá documentos associados devido ao CASCADE
        conversation.delete()
        messages.success(request, "Chat e documentos associados excluídos com sucesso")
        return redirect('chat_list')
    return render(request, 'chat/delete_confirm.html', {'conversation': conversation})
