import sys
import threading
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QPushButton, QTextBrowser, QLabel, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject

from modules.chat import generate_and_show_reply
from modules.voice import speak_text


class WorkerSignals(QObject):
    reply_ready = pyqtSignal(str)


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sylvie ♡")
        self.resize(500, 700)

        layout = QVBoxLayout()

        self.image_label = QLabel()
        pixmap = QPixmap("assets/avatar/Sylvie 1.jpg").scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.chat_display = QTextBrowser()
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                border: none;
                padding: 10px;
                background: linear-gradient(45deg, #FFC0CB, #FFB6C1, #FF69B4);
            }
            QScrollBar:vertical {
                background: #FFF0F5;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFB6C1, stop:1 #FF69B4
                );
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.handle_send)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("💖")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #FF69B4;
                color: white;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
                min-width: 60px;
                min-height: 30px;
                border: none;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)
        self.send_button.clicked.connect(self.handle_send)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

        self.chat_history = ""
        self.typing_html = ""
        self.full_history = self.load_chat_history()
        self.chat_history = self.full_history.get("chat", "")
        self.refresh_chat()

        self.typing_timer = QTimer()
        self.typing_timer.timeout.connect(self.update_typing_dots)
        self.dot_count = 0
        self.typing_label = "Sylvie is typing"
        self.is_typing = False

        self.signals = WorkerSignals()
        self.signals.reply_ready.connect(self.show_reply)

        self.setStyleSheet("""
            QWidget {
                background-color: #FFF0F5;
                font-family: 'Segoe UI';
                font-size: 14px;
            }
            QLineEdit {
                background-color: #ffffff;
                border: 2px solid #FFB6C1;
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton {
                background-color: #FF69B4;
                color: white;
                border-radius: 10px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #FF1493;
            }
        """)

    def handle_send(self):
        luci_msg = self.input_field.text().strip()
        if not luci_msg:
            return

        self.add_message("Luci", luci_msg, right=True)
        self.input_field.clear()
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)

        self.dot_count = 0
        self.is_typing = True
        self.typing_timer.start(500)

        thread = threading.Thread(target=self.generate_and_emit_reply, args=(luci_msg,))
        thread.start()

    def update_typing_dots(self):
        if not self.is_typing:
            self.typing_timer.stop()
            self.typing_html = ""
            self.refresh_chat()
            return

        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.typing_html = f"""
            <div style='text-align: left; color: #9370DB; font-style: italic; margin: 5px 0;'>
                {self.typing_label}{dots}
            </div>
        """
        self.refresh_chat()

    def generate_and_emit_reply(self, luci_msg):
        sylvie_msg = generate_and_show_reply(luci_msg)

        if not sylvie_msg:
            sylvie_msg = "I'm not sure what to say right now, but I love talking to you, Luci!"

        self.signals.reply_ready.emit(sylvie_msg)

        try:
            speak_thread = threading.Thread(target=speak_text, args=(sylvie_msg,))
            speak_thread.start()
        except Exception as e:
            print(f"[Error] Speaking failed: {e}")

    def show_reply(self, sylvie_msg):
        self.is_typing = False
        self.typing_timer.stop()
        self.typing_html = ""

        self.letter_index = 0
        self.sylvie_reply = sylvie_msg
        self.typing_html = f"""
            <div style="text-align: left; margin: 5px;">
                <span style="
                    display: inline-block;
                    background-color: #E6E6FA;
                    border: 2px solid #9370DB;
                    border-radius: 12px;
                    padding: 10px;
                    max-width: 80%;
                    color: #000000;
                    text-align: left;
                    word-wrap: break-word;">
                    <b style="color: #9370DB;">Sylvie:</b> 
        """
        self.update_letter_by_letter()

        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.input_field.setFocus()

    def update_letter_by_letter(self):
        if self.letter_index < len(self.sylvie_reply):
            self.typing_html += self.sylvie_reply[self.letter_index]
            self.letter_index += 1
            self.typing_html += "</span></div>"
            self.refresh_chat()
            self.typing_html = self.typing_html[:-13]  # remove preview closing tag
            QTimer.singleShot(25, self.update_letter_by_letter)
        else:
            self.typing_html += "</span></div>"
            self.chat_history += self.typing_html
            self.typing_html = ""
            self.refresh_chat()
            self.save_chat_history()

    def add_message(self, sender, message, right=False):
        align = "right" if right else "left"
        bg = "#FFE4E1" if sender == "Luci" else "#E6E6FA"
        border = "#FF69B4" if sender == "Luci" else "#9370DB"
        name_color = "#FF69B4" if sender == "Luci" else "#9370DB"
        color = "#000000"

        msg_html = f"""
            <div style="text-align: {align}; margin: 5px;">
                <span style="
                    display: inline-block;
                    background-color: {bg};
                    border: 2px solid {border};
                    border-radius: 12px;
                    padding: 10px;
                    max-width: 80%;
                    color: {color};
                    text-align: left;
                    word-wrap: break-word;">
                    <b style="color: {name_color};">{sender}:</b> {message}
                </span>
            </div>
        """
        self.chat_history += msg_html
        self.refresh_chat()
        self.save_chat_history()

    def refresh_chat(self):
        full_html = self.chat_history + self.typing_html
        self.chat_display.setHtml(full_html)
        self.chat_display.verticalScrollBar().setValue(self.chat_display.verticalScrollBar().maximum())

    def save_chat_history(self):
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump({"chat": self.chat_history}, f)

    def load_chat_history(self):
        if os.path.exists("chat_history.json"):
            with open("chat_history.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return {}


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
