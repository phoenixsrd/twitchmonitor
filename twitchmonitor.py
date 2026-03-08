#!/usr/bin/env python3

import sys
import time
import platform
import subprocess
import webbrowser
import urllib.request
import urllib.parse
import json
import os

CHANNEL_NAME    = "nome_do_canal"
CLIENT_ID       = "SEU_CLIENT_ID"
CLIENT_SECRET   = "SEU_CLIENT_SECRET"
CHECK_INTERVAL  = 60

TWITCH_URL      = f"https://www.twitch.tv/{CHANNEL_NAME}"
TWITCH_APP_URL  = f"twitch://stream/{CHANNEL_NAME}"
TOKEN_URL       = "https://id.twitch.tv/oauth2/token"
STREAMS_URL     = "https://api.twitch.tv/helix/streams"

os_name = platform.system()


def log(msg: str):
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")


def get_access_token() -> str:
    data = urllib.parse.urlencode({
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type":    "client_credentials",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def is_live(token: str) -> bool:
    params = urllib.parse.urlencode({"user_login": CHANNEL_NAME})
    url = f"{STREAMS_URL}?{params}"
    req = urllib.request.Request(url, headers={
        "Client-ID":     CLIENT_ID,
        "Authorization": f"Bearer {token}",
    })
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
        return len(data.get("data", [])) > 0


def send_notification(title: str, message: str):
    try:
        if os_name == "Windows":
            script = (
                f'[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, '
                f'ContentType = WindowsRuntime] | Out-Null; '
                f'$template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent('
                f'[Windows.UI.Notifications.ToastTemplateType]::ToastText02); '
                f'$template.GetElementsByTagName("text")[0].AppendChild($template.CreateTextNode("{title}")); '
                f'$template.GetElementsByTagName("text")[1].AppendChild($template.CreateTextNode("{message}")); '
                f'$toast = [Windows.UI.Notifications.ToastNotification]::new($template); '
                f'[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("TwitchMonitor").Show($toast);'
            )
            subprocess.Popen(["powershell", "-Command", script],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        elif os_name == "Darwin":
            subprocess.Popen(
                ["osascript", "-e",
                 f'display notification "{message}" with title "{title}" sound name "Glass"'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )

        elif os_name == "Linux":
            subprocess.Popen(
                ["notify-send", title, message, "--icon=dialog-information"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
    except Exception as e:
        log(f"⚠️  Notificação não enviada: {e}")


def is_termux() -> bool:
    return "com.termux" in os.environ.get("PREFIX", "") or \
           os.path.exists("/data/data/com.termux")


def open_stream():
    log(f"🔴 {CHANNEL_NAME} entrou ao vivo! Abrindo stream...")
    send_notification("🔴 Live iniciada!", f"{CHANNEL_NAME} está ao vivo na Twitch!")

    if is_termux():
        opened = False

        try:
            result = subprocess.run(
                ["termux-open-url", TWITCH_APP_URL],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
            )
            if result.returncode == 0:
                log("📱 Aberto no app da Twitch via termux-open-url.")
                opened = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        if not opened:
            try:
                result = subprocess.run(
                    ["am", "start", "-a", "android.intent.action.VIEW", "-d", TWITCH_APP_URL],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
                )
                if result.returncode == 0:
                    log("📱 Aberto no app da Twitch via am start.")
                    opened = True
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass

        if not opened:
            log("🌐 App não encontrado, abrindo no navegador...")
            try:
                subprocess.Popen(["termux-open-url", TWITCH_URL],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                webbrowser.open(TWITCH_URL)

    elif os_name == "Windows":
        os.startfile(TWITCH_URL)

    elif os_name == "Darwin":
        subprocess.Popen(["open", TWITCH_URL])

    elif os_name == "Linux":
        try:
            subprocess.Popen(["xdg-open", TWITCH_URL],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            webbrowser.open(TWITCH_URL)

    else:
        webbrowser.open(TWITCH_URL)


def validate_config():
    if CHANNEL_NAME == "nome_do_canal":
        print("❌ Edite CHANNEL_NAME com o nome do canal que quer monitorar.")
        sys.exit(1)
    if CLIENT_ID == "SEU_CLIENT_ID" or CLIENT_SECRET == "SEU_CLIENT_SECRET":
        print("❌ Configure CLIENT_ID e CLIENT_SECRET.")
        print("   → Acesse https://dev.twitch.tv/console e crie um app.")
        sys.exit(1)


def main():
    validate_config()

    print("=" * 55)
    print(f"  🎮 Twitch Monitor  —  Canal: {CHANNEL_NAME}")
    print(f"  💻 Sistema: {os_name}  |  Verificando a cada {CHECK_INTERVAL}s")
    print("=" * 55)
    print("  Pressione Ctrl+C para parar.\n")

    token = get_access_token()
    log("✅ Token obtido. Iniciando monitoramento...")

    was_live = False
    token_refresh_counter = 0

    while True:
        try:
            token_refresh_counter += 1
            if token_refresh_counter >= (3600 // CHECK_INTERVAL):
                token = get_access_token()
                token_refresh_counter = 0
                log("🔄 Token renovado.")

            live = is_live(token)

            if live and not was_live:
                open_stream()
                was_live = True
            elif not live and was_live:
                log(f"⚫ {CHANNEL_NAME} encerrou a live.")
                was_live = False
            else:
                status = "🔴 AO VIVO" if live else "⚫ offline"
                log(f"Canal {CHANNEL_NAME} está {status}. Próxima verificação em {CHECK_INTERVAL}s...")

        except KeyboardInterrupt:
            print("\n\n👋 Monitoramento encerrado.")
            sys.exit(0)
        except Exception as e:
            log(f"⚠️  Erro: {e}. Tentando novamente em {CHECK_INTERVAL}s...")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()