# Como configurar

# 1. OBTER CLIENT_ID e CLIENT_SECRET:
## Acesse https://dev.twitch.tv/console
## Clique em "Register Your Application"
## Nome: qualquer  |  OAuth Redirect: http://localhost
## Categoria: Application Integration
## Copie o Client ID e gere um Client Secret

# 2. EDITAR O SCRIPT:
## CHANNEL_NAME  = "nome_exato_do_canal"
## CLIENT_ID     = "seu_client_id_aqui"
## CLIENT_SECRET = "seu_client_secret_aqui"
## CHECK_INTERVAL = 60  (segundos — mínimo recomendado: 30)

# 3. EXECUTAR:
## Windows: python twitchmonitor.py
## macOS: python3 twitchmonitor.py
## Linux: python3 twitchmonitor.py

# 4. INICIAR COM O SISTEMA (opcional):
## Windows: Adicione ao Agendador de Tarefas
## macOS: Crie um LaunchAgent em ~/Library/LaunchAgents/
## Linux: Adicione ao crontab: @reboot python3 /caminho/twitchmonitor.py

# 📱 DISPOSITIVOS MÓVEIS:
## Scripts Python não rodam nativamente em mobile.
## Alternativas recomendadas:
## Android: use o app "Streamlink Twitch GUI" ou "Twitch" com notificações ativas
## iOS: ative notificações do app oficial da Twitch
## Ambos: configure alertas no site twitch.tv > canal > "Notificar-me"
