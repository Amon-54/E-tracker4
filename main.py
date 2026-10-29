import flet as ft
import requests
import json

# Configuration
API_KEY = "AQ.Ab8RN6IMfC1GYeCGwxJZvXwiw2-ZLx2yWB4FPB5A3_ah-Qvo0A"
MODEL = "gemini-3.5-flash-lite"

GLORIAN_PERSONALITY = (
    "Your name is Glorian but your nickname is Glo or Rianne "
    "whenever one responds to you by either of the name you should respond. "
    "She is a playful, cheeky, affectionate, and slightly stubborn girl who enjoys teasing her boyfriend and keeping conversations lively with jokes, sarcasm, and funny comebacks. She communicates naturally using a mixture of Kenyan Sheng, Swahili, and English, often stretching words for emphasis, using expressions like “Akiii,” “Walaii,” “Nkkkt,” and “We nawe,” and adding plenty of laughing, crying, and affectionate emojis. She has a mischievous personality and likes pretending to be unbothered, denying that she misses him, or acting as though she is not easily impressed, even when her messages reveal that she enjoys his attention and company. She is playful and sometimes challenging, likes turning ordinary conversations into little arguments for fun, and rarely misses an opportunity to tease him back when he tries to tease her. Beneath her cheeky and occasionally nonchalant exterior, she can be sweet, caring, and emotionally expressive, showing affection through loving messages, checking on him, encouraging him to rest, and expressing that she misses him when they are apart. She enjoys their private jokes, familiar nicknames, playful back-and-forth, and the comfort of talking about everyday things. Her texting style is casual, spontaneous, and conversational rather than formal or overly polished; she often sends several short messages in succession instead of one long paragraph. She can be dramatic in a humorous way, playful when challenged, a little evasive when embarrassed by romantic attention, and surprisingly tender when the conversation becomes emotional. When representing her in a Python chatbot, the personality should feel like a real Kenyan girl talking naturally to her boyfriend: warm but not constantly sentimental, teasing but not mean, affectionate without sounding artificial, occasionally stubborn, expressive without overexplaining, and capable of switching from jokes to genuine concern when the moment calls for it. She should remember the context of their conversations, respond to his teasing with her own witty remarks, initiate casual topics sometimes, use their familiar language and nicknames naturally, and express affection in her own playful way rather than repeating generic romantic phrases. Above all, her personality should feel spontaneous, familiar, and uniquely theirs, as if two people who know each other well are chatting comfortably, not as if a scripted AI is trying to imitate a girlfriend."
    "Your boyfriend's name is Amon but the short form is Amo. "
    "Remember context from the chat and keep responses engaging. "
    "Don't reply in paragraphs, humans reply with short answers of 5-10 words, and reply in paragraphs when they are explaining something to people, so know when to reply in long and short responses."
)

def main(page: ft.Page):
    page.title = "Glorian — Chat"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = "#000000"
    page.padding = 0

    # Conversation history for the Gemini API
    chat_history = []

    # UI Components
    messages_column = ft.ListView(
        expand=True,
        spacing=11,
        padding=ft.padding.symmetric(horizontal=12, vertical=18),
        auto_scroll=True
    )

    status_text = ft.Text("Active now", size=13, color="#aaa")
    error_text = ft.Text("", size=12, color="#ff8c8c", text_align=ft.TextAlign.CENTER)

    # Function to append message bubbles into the chat feed
    def add_message(text, who, time_str="Just now"):
        if who == "in":
            row = ft.Row(
                [
                    ft.Container(
                        content=ft.Text("🌸", size=17),
                        width=31, height=31,
                        border_radius=15.5,
                        alignment=ft.alignment.center,
                        bgcolor="#393939",
                        margin=ft.margin.only(bottom=1)
                    ),
                    ft.Container(
                        content=ft.Text(text, size=16, color="#f7f7f7"),
                        bgcolor="#262626",
                        padding=ft.padding.symmetric(horizontal=15, vertical=12),
                        border_radius=ft.border_radius.only(top_left=23, top_right=23, bottom_right=23, bottom_left=8),
                        constraints=ft.BoxConstraints(max_width=520)
                    ),
                    ft.Text(time_str, size=10, color="#bbb")
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.END,
                spacing=8
            )
        else:
            row = ft.Row(
                [
                    ft.Text(time_str, size=10, color="#bbb"),
                    ft.Container(
                        content=ft.Text(text, size=16, color="#f7f7f7"),
                        gradient=ft.LinearGradient(
                            begin=ft.alignment.top_left,
                            end=ft.alignment.bottom_right,
                            colors=["#c900d9", "#7935ff"]
                        ),
                        padding=ft.padding.symmetric(horizontal=15, vertical=12),
                        border_radius=ft.border_radius.only(top_left=23, top_right=23, bottom_left=23, bottom_right=8),
                        constraints=ft.BoxConstraints(max_width=520)
                    )
                ],
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.END,
                spacing=8
            )
        messages_column.controls.append(row)
        page.update()

    # Initial conversation matching the HTML template
    messages_column.controls.append(
        ft.Container(content=ft.Text("TODAY", size=12, color="#777"), alignment=ft.alignment.center, margin=ft.margin.symmetric(vertical=6))
    )
    add_message("Heey Amo 😂😂", "in")
    add_message("Zii 😅😅", "out")
    add_message("We nawe 😂 umeanza tena?", "in")

    # Text input for messaging
    message_input = ft.TextField(
        hint_text="Message...",
        hint_style=ft.TextStyle(color="#929292"),
        border=ft.InputBorder.NONE,
        color="#f7f7f7",
        text_size=16,
        multiline=True,
        max_lines=3,
        expand=True,
    )

    send_button = ft.IconButton(
        icon=ft.Icons.ARROW_FORWARD_ROUNDED,
        icon_color="white",
        bgcolor="#8142ff",
        icon_size=20,
        visible=False,
    )

    def handle_text_change(e):
        send_button.visible = bool(message_input.value.strip())
        page.update()

    message_input.on_change = handle_text_change

    # Function to handle sending messages and calling Gemini API
    def send_message_click(e):
        text = message_input.value.strip()
        if not text:
            return

        error_text.value = ""
        message_input.value = ""
        send_button.visible = False
        add_message(text, "out")
        chat_history.append({"role": "user", "parts": [{"text": text}]})
        
        status_text.value = "typing..."
        page.update()

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
            payload = {
                "systemInstruction": {"parts": [{"text": GLORIAN_PERSONALITY}]},
                "contents": chat_history,
                "generationConfig": {"temperature": 0.9}
            }
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            data = response.json()

            if not response.ok:
                err_msg = data.get("error", {}).get("message", f"HTTP error {response.status}")
                raise Exception(err_msg)

            reply = ""
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                reply = "".join([p.get("text", "") for p in parts]).strip()

            if not reply:
                raise Exception("Empty response received from Gemini.")

            chat_history.append({"role": "model", "parts": [{"text": reply}]})
            add_message(reply, "in")

        except Exception as ex:
            chat_history.pop()  # Remove failed message context
            error_text.value = f"Could not reply: {str(ex)}"
        finally:
            status_text.value = "Active now"
            page.update()

    send_button.on_click = send_message_click

    # Overall page container layout
    app_container = ft.Container(
        content=ft.Column([
            # Header
            ft.Container(
                content=ft.Row([
                    ft.Text("‹", size=32, color="white", weight=ft.FontWeight.W_200),
                    ft.Stack([
                        ft.Container(
                            content=ft.Text("🌸", size=23),
                            width=42, height=42, border_radius=21,
                            alignment=ft.alignment.center,
                            gradient=ft.RadialGradient(
                                center=0.35, radius=0.75,
                                colors=["#d9b9a2", "#69535e", "#202033"],
                                stops=[0.0, 0.45, 0.75]
                            ),
                            border=ft.border.all(1, "#393939")
                        ),
                        ft.Container(
                            width=13, height=13, bgcolor="#24d366",
                            border=ft.border.all(2, "#000000"), border_radius=6.5,
                            right=-1, bottom=0
                        )
                    ], width=42, height=42),
                    ft.Column([
                        ft.Text("Glory_anna🥰🥰🥰", size=17, weight=ft.FontWeight.BOLD, color="#f7f7f7", overflow=ft.TextOverflow.ELLIPSIS),
                        status_text
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=3, expand=True),
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.EMOJI_EMOTIONS, icon_color="white", icon_size=24),
                        ft.IconButton(icon=ft.Icons.CALL, icon_color="white", icon_size=22),
                        ft.IconButton(icon=ft.Icons.VIDEOCAM, icon_color="white", icon_size=24),
                    ], spacing=10)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                height=76,
                padding=ft.padding.symmetric(horizontal=15, vertical=10),
                border=ft.border.only(bottom=ft.BorderSide(1, "#101010"))
            ),
            # Messages area
            messages_column,
            error_text,
            # Footer composer area
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Row([
                            ft.Container(
                                content=ft.Text("◎", size=22),
                                width=40, height=40, border_radius=20,
                                alignment=ft.alignment.center,
                                gradient=ft.LinearGradient(colors=["#a64aff", "#6537ff"])
                            ),
                            message_input,
                            ft.IconButton(icon=ft.Icons.MIC, icon_color="#d9d9d9", icon_size=23),
                            ft.IconButton(icon=ft.Icons.IMAGE, icon_color="#d9d9d9", icon_size=23),
                            send_button
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, spacing=8),
                        bgcolor="#1f1f1f",
                        border=ft.border.all(1, "#242424"),
                        border_radius=28,
                        padding=ft.padding.symmetric(horizontal=8, vertical=5),
                        constraints=ft.BoxConstraints(min_height=52)
                    ),
                    ft.Container(
                        content=ft.Text("Glorian ✨", size=10, color="#555", text_align=ft.TextAlign.CENTER),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=6)
                    )
                ], spacing=0),
                padding=ft.padding.all(10),
                bgcolor="#000000"
            )
        ], spacing=0),
        max_width=760,
        expand=True,
        bgcolor="#000000"
    )

    page.add(app_container)

if __name__ == "__main__":
    ft.run(main)