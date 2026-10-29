"""Графічний інтерфейс APEXUS 1V (PySide6)."""
from __future__ import annotations

import dataclasses
from functools import partial

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRectF, Qt, QTimer, Signal
from PySide6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from chat import ChatStore, ChatWorker, TestWorker
from settings import CUSTOM_PRESET, PRESETS, Settings, normalize_url, provider_name

STYLE = """
QMainWindow, #root { background: #08080e; }
QWidget { color: #e6e8f2; }
QLabel { background: transparent; }

#sidebar { background: #0e0f19; border-right: 1px solid #22243a; }
#brand { color: #ffffff; font-size: 17px; font-weight: 700; }
#brandSub { color: #7f86ad; font-size: 11px; }
#sectionLabel { color: #6c7299; font-size: 11px; font-weight: 600; }

#header { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0c0d17, stop:1 #15122b);
          border-bottom: 1px solid #22243a; }
#title { color: #1e90ff; background: transparent; }
#subtitle { color: #8d93b8; font-size: 12px; }

#banner { background: #2a2110; border: 1px solid #6d5316; border-radius: 12px; }
#banner QLabel { color: #f4d58d; }

QScrollArea { border: none; background: transparent; }
#chatHost { background: transparent; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #2b2f4d; border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #3a4070; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

#userBubble { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #2563eb, stop:1 #6d3fd8);
              border-radius: 18px; }
#aiBubble { background: #151728; border: 1px solid #262a44; border-radius: 18px; }
#errBubble { background: #2a1218; border: 1px solid #7a2433; border-radius: 18px; }
#bubbleName { color: #9aa3d6; font-size: 11px; font-weight: 700; }
#userBubble #bubbleName { color: #d6e4ff; }
#errBubble #bubbleName { color: #ff8a9a; }
#welcome { color: #9aa0c6; }

#typing { color: #8fb4ff; font-size: 13px; padding-left: 22px; }
#status { color: #8d93b8; font-size: 12px; padding-left: 22px; }

#inputFrame { background: #11121f; border: 1px solid #2a2d48; border-radius: 22px; }
#inputBox { background: transparent; border: none; padding: 6px 4px; selection-background-color: #2f5fd0; }

QPushButton { border: none; outline: 0; }
QPushButton#primaryBtn { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2f8bff, stop:1 #8b5cf6);
    color: white; border-radius: 14px; padding: 12px 16px; font-weight: 700; }
QPushButton#primaryBtn:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #55a2ff, stop:1 #a07bfa); }
QPushButton#primaryBtn:pressed { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #1f6fd6, stop:1 #6d42d8); }
QPushButton#primaryBtn:disabled { background: #232538; color: #6c7299; }
QPushButton#sendBtn { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2f8bff, stop:1 #8b5cf6);
    color: white; border-radius: 18px; padding: 0 22px; font-weight: 700; min-height: 40px; }
QPushButton#sendBtn:hover { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #55a2ff, stop:1 #a07bfa); }
QPushButton#sendBtn:disabled { background: #232538; color: #6c7299; }
QPushButton#ghostBtn { background: #151728; border: 1px solid #272a42; border-radius: 12px;
    padding: 10px 14px; color: #c9cde6; text-align: left; }
QPushButton#ghostBtn:hover { border-color: #2f8bff; background: #191c33; }
QPushButton#bannerBtn { background: #5a4513; color: #ffe3a3; border-radius: 10px; padding: 6px 14px; }
QPushButton#bannerBtn:hover { background: #75591a; }

QListWidget { background: transparent; border: none; outline: 0; }
QListWidget::item { padding: 11px 12px; border-radius: 10px; margin: 2px 0; color: #b8bdd9; }
QListWidget::item:hover { background: #181a2d; }
QListWidget::item:selected { color: white;
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 rgba(47,139,255,90), stop:1 rgba(139,92,246,90)); }

QDialog { background: #0e0f19; }
QLineEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    background: #151728; border: 1px solid #2a2d48; border-radius: 10px; padding: 7px 10px;
    selection-background-color: #2f5fd0; }
QLineEdit:focus, QPlainTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus { border-color: #2f8bff; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView { background: #151728; border: 1px solid #2a2d48; selection-background-color: #2f5fd0; outline: 0; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 5px; border: 1px solid #3a3f66; background: #151728; }
QCheckBox::indicator:checked { background: #2f8bff; border-color: #2f8bff; }
QMenu { background: #151728; border: 1px solid #2a2d48; border-radius: 10px; padding: 6px; }
QMenu::item { padding: 8px 22px; border-radius: 6px; }
QMenu::item:selected { background: #2a3160; }
QMessageBox, QInputDialog { background: #0e0f19; }
QToolTip { background: #151728; color: #e6e8f2; border: 1px solid #2a2d48; }
"""


class LogoWidget(QWidget):
    """Логотип APEXUS: градієнтний заокруглений квадрат із літерою «A»."""

    def __init__(self, size: int = 44, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        grad = QLinearGradient(r.topLeft(), r.bottomRight())
        grad.setColorAt(0.0, QColor("#2f8bff"))
        grad.setColorAt(1.0, QColor("#8b5cf6"))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(r, r.width() * 0.28, r.width() * 0.28)
        pen = QPen(QColor("white"), r.width() * 0.09, Qt.PenStyle.SolidLine,
                   Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
        p.setPen(pen)
        p.setBrush(Qt.BrushStyle.NoBrush)
        w, h, x0, y0 = r.width(), r.height(), r.left(), r.top()
        path = QPainterPath()
        path.moveTo(x0 + w * 0.27, y0 + h * 0.76)
        path.lineTo(x0 + w * 0.50, y0 + h * 0.24)
        path.lineTo(x0 + w * 0.73, y0 + h * 0.76)
        path.moveTo(x0 + w * 0.36, y0 + h * 0.58)
        path.lineTo(x0 + w * 0.64, y0 + h * 0.58)
        p.drawPath(path)
        p.end()


class InputBox(QPlainTextEdit):
    """Поле введення: Enter — відправити, Shift+Enter — новий рядок."""

    submit = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("inputBox")
        self.setPlaceholderText("Напишіть повідомлення… (Enter — надіслати, Shift+Enter — новий рядок)")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.textChanged.connect(self._fit)
        self._fit()

    def _fit(self) -> None:
        lines = max(1, int(self.document().size().height()))
        h = lines * self.fontMetrics().lineSpacing() + 24
        self.setFixedHeight(max(46, min(h, 150)))

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and not (
            event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        ):
            self.submit.emit()
            return
        super().keyPressEvent(event)


class MessageRow(QWidget):
    """Один рядок чату з «бульбашкою» повідомлення."""

    NAMES = {"user": "Ви", "assistant": "APEXUS", "error": "Помилка"}
    IDS = {"user": "userBubble", "assistant": "aiBubble", "error": "errBubble"}

    def __init__(self, role: str, text: str, parent=None):
        super().__init__(parent)
        self.role = role
        lay = QHBoxLayout(self)
        lay.setContentsMargins(10, 5, 10, 5)

        self.bubble = QFrame()
        self.bubble.setObjectName(self.IDS[role])
        inner = QVBoxLayout(self.bubble)
        inner.setContentsMargins(16, 10, 16, 12)
        inner.setSpacing(4)

        name = QLabel(self.NAMES[role])
        name.setObjectName("bubbleName")
        body = QLabel()
        body.setWordWrap(True)
        body.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        body.setOpenExternalLinks(True)
        if role == "assistant":
            body.setTextFormat(Qt.TextFormat.MarkdownText)
        else:
            body.setTextFormat(Qt.TextFormat.PlainText)
        body.setText(text)
        inner.addWidget(name)
        inner.addWidget(body)

        if role == "user":
            lay.addStretch(1)
            lay.addWidget(self.bubble)
        else:
            lay.addWidget(self.bubble)
            lay.addStretch(1)

    def set_max_width(self, width: int) -> None:
        self.bubble.setMaximumWidth(width)


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._orig = settings
        self._test: TestWorker | None = None
        self.setWindowTitle("Налаштування APEXUS 1V")
        self.setMinimumWidth(580)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 18)
        root.setSpacing(14)
        head = QLabel("Налаштування")
        head.setStyleSheet("font-size: 20px; font-weight: 700; color: #1e90ff;")
        root.addWidget(head)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.preset_box = QComboBox()
        self.preset_box.addItems(list(PRESETS.keys()))

        self.url_edit = QLineEdit(settings.api_url)
        self.url_edit.setPlaceholderText("https://api.example.com/v1/chat/completions")
        self.model_edit = QLineEdit(settings.model)
        self.model_edit.setPlaceholderText("Назва моделі, напр. deepseek-chat")

        self.key_edit = QLineEdit(settings.api_key)
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_edit.setPlaceholderText("API-ключ вашого сервісу (для Ollama не потрібен)")
        self.show_key = QCheckBox("Показати ключ")
        self.show_key.toggled.connect(
            lambda on: self.key_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password
            )
        )

        self.test_btn = QPushButton("Перевірити зʼєднання")
        self.test_btn.setObjectName("ghostBtn")
        self.test_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.test_btn.clicked.connect(self._run_test)
        self.test_label = QLabel("")
        self.test_label.setWordWrap(True)

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setDecimals(1)
        self.temp_spin.setValue(settings.temperature)

        self.tokens_spin = QSpinBox()
        self.tokens_spin.setRange(256, 8192)
        self.tokens_spin.setSingleStep(256)
        self.tokens_spin.setValue(settings.max_tokens)

        self.prompt_edit = QPlainTextEdit(settings.system_prompt)
        self.prompt_edit.setFixedHeight(80)

        self.font_spin = QSpinBox()
        self.font_spin.setRange(11, 22)
        self.font_spin.setSuffix(" px")
        self.font_spin.setValue(settings.font_size)

        self.anim_check = QCheckBox("Плавні анімації")
        self.anim_check.setChecked(settings.animations)

        form.addRow("Сервіс:", self.preset_box)
        form.addRow("Адреса API:", self.url_edit)
        form.addRow("Модель:", self.model_edit)
        form.addRow("API-ключ:", self.key_edit)
        form.addRow("", self.show_key)
        form.addRow("", self.test_btn)
        form.addRow("", self.test_label)
        form.addRow("Температура:", self.temp_spin)
        form.addRow("Макс. токенів:", self.tokens_spin)
        form.addRow("Системна роль:", self.prompt_edit)
        form.addRow("Розмір шрифту:", self.font_spin)
        form.addRow("", self.anim_check)
        root.addLayout(form)

        hint = QLabel(
            "Ключ має бути від того ж сервісу, що й адреса API. Підтримуються всі сервіси з форматом "
            "OpenAI /chat/completions. Ключ зберігається лише локально на цьому комп'ютері. "
            "Якщо поле ключа порожнє, береться змінна середовища DEEPSEEK_API_KEY."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #7f86ad; font-size: 12px;")
        root.addWidget(hint)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        cancel = QPushButton("Скасувати")
        cancel.setObjectName("ghostBtn")
        save = QPushButton("Зберегти")
        save.setObjectName("primaryBtn")
        save.setDefault(True)
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self._on_save)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        root.addLayout(buttons)

        # початковий вибір пресету за адресою
        current = normalize_url(settings.api_url)
        chosen = CUSTOM_PRESET
        for name, (url, _model) in PRESETS.items():
            if url and normalize_url(url) == current:
                chosen = name
                break
        self.preset_box.setCurrentText(chosen)
        self.preset_box.currentTextChanged.connect(self._apply_preset)

    def _apply_preset(self, name: str) -> None:
        url, model = PRESETS.get(name, ("", ""))
        if name != CUSTOM_PRESET:
            self.url_edit.setText(url)
            self.model_edit.setText(model)
        self.test_label.setText("")

    def _current(self) -> Settings:
        return dataclasses.replace(
            self._orig,
            model=self.model_edit.text().strip(),
            api_url=normalize_url(self.url_edit.text()),
            api_key=self.key_edit.text().strip(),
            temperature=round(self.temp_spin.value(), 1),
            max_tokens=self.tokens_spin.value(),
            system_prompt=self.prompt_edit.toPlainText().strip(),
            font_size=self.font_spin.value(),
            animations=self.anim_check.isChecked(),
        )

    def _set_result(self, ok: bool, text: str) -> None:
        color = "#5fd68a" if ok else "#ff8a9a"
        self.test_label.setStyleSheet(f"color: {color};")
        self.test_label.setText(text)

    def _run_test(self) -> None:
        if self._test is not None and self._test.isRunning():
            return
        cfg = self._current()
        if not cfg.api_url or not cfg.model:
            self._set_result(False, "Вкажіть адресу API та назву моделі.")
            return
        self.test_btn.setEnabled(False)
        self.test_label.setStyleSheet("color: #8fb4ff;")
        self.test_label.setText("Перевіряю зʼєднання…")
        self._test = TestWorker(cfg)
        self._test.done.connect(self._on_test_done)
        self._test.start()

    def _on_test_done(self, ok: bool, text: str) -> None:
        self.test_btn.setEnabled(True)
        self._set_result(ok, text)

    def _on_save(self) -> None:
        cfg = self._current()
        if not cfg.api_url or not cfg.model:
            self._set_result(False, "Вкажіть адресу API та назву моделі.")
            return
        self.accept()

    def done(self, result: int) -> None:
        if self._test is not None and self._test.isRunning():
            self._test.terminate()
            self._test.wait(500)
        super().done(result)

    def result_settings(self) -> Settings:
        return self._current()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = Settings.load()
        self.store = ChatStore()
        self.current_id: str | None = None
        self.busy = False
        self.busy_chat_id: str | None = None
        self._workers: list[ChatWorker] = []
        self.rows: list[MessageRow] = []
        self.welcome: QLabel | None = None
        self._updating_list = False
        self._dots = 0

        self.setWindowTitle("APEXUS 1V — AI-помічник")
        self.resize(1280, 820)
        self.setMinimumSize(900, 600)

        self._build_ui()
        self.apply_style()
        self.update_banner()
        self.refresh_list()

        chats = self.store.sorted_chats()
        if chats:
            self.open_chat(chats[0].id)
        else:
            self.new_chat()

    # ------------------------------------------------------------------ UI
    def _build_ui(self) -> None:
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        outer = QHBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # --- бічна панель
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(290)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(16, 18, 16, 16)
        sb.setSpacing(12)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(12)
        brand_row.addWidget(LogoWidget(46))
        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        b1 = QLabel("APEXUS AI")
        b1.setObjectName("brand")
        b2 = QLabel("Розумний помічник")
        b2.setObjectName("brandSub")
        brand_text.addWidget(b1)
        brand_text.addWidget(b2)
        brand_row.addLayout(brand_text)
        brand_row.addStretch(1)
        sb.addLayout(brand_row)

        self.new_btn = QPushButton("＋  Новий чат")
        self.new_btn.setObjectName("primaryBtn")
        self.new_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_btn.clicked.connect(self.new_chat)
        sb.addWidget(self.new_btn)

        lbl = QLabel("ІСТОРІЯ ЧАТІВ")
        lbl.setObjectName("sectionLabel")
        sb.addWidget(lbl)

        self.list = QListWidget()
        self.list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self._list_menu)
        self.list.currentItemChanged.connect(self._on_item_changed)
        sb.addWidget(self.list, 1)

        self.settings_btn = QPushButton("⚙  Налаштування")
        self.settings_btn.setObjectName("ghostBtn")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.open_settings)
        self.clear_btn = QPushButton("🗑  Очистити історію")
        self.clear_btn.setObjectName("ghostBtn")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.clicked.connect(self.clear_history)
        sb.addWidget(self.settings_btn)
        sb.addWidget(self.clear_btn)
        outer.addWidget(sidebar)

        # --- основна область
        main = QWidget()
        mv = QVBoxLayout(main)
        mv.setContentsMargins(0, 0, 0, 0)
        mv.setSpacing(0)

        header = QFrame()
        header.setObjectName("header")
        hv = QVBoxLayout(header)
        hv.setContentsMargins(20, 14, 20, 12)
        hv.setSpacing(0)

        self.title = QLabel("APEXUS 1V")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tf = QFont("Segoe UI")
        tf.setPixelSize(52)
        tf.setWeight(QFont.Weight.Black)
        tf.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 7)
        self.title.setFont(tf)
        self.glow = QGraphicsDropShadowEffect(self.title)
        self.glow.setColor(QColor("#1e90ff"))
        self.glow.setOffset(0, 0)
        self.glow.setBlurRadius(28)
        self.title.setGraphicsEffect(self.glow)
        self.glow_anim = QPropertyAnimation(self.glow, b"blurRadius", self)
        self.glow_anim.setDuration(3200)
        self.glow_anim.setKeyValueAt(0.0, 18)
        self.glow_anim.setKeyValueAt(0.5, 46)
        self.glow_anim.setKeyValueAt(1.0, 18)
        self.glow_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.glow_anim.setLoopCount(-1)

        self.subtitle = QLabel()
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hv.addWidget(self.title)
        hv.addWidget(self.subtitle)
        mv.addWidget(header)

        # банер про відсутній ключ
        self.banner = QFrame()
        self.banner.setObjectName("banner")
        bl = QHBoxLayout(self.banner)
        bl.setContentsMargins(14, 8, 14, 8)
        bl_text = QLabel(
            "API-ключ не знайдено. Введіть його в налаштуваннях "
            "(або задайте змінну середовища DEEPSEEK_API_KEY)."
        )
        bl_text.setWordWrap(True)
        bl_btn = QPushButton("Налаштування")
        bl_btn.setObjectName("bannerBtn")
        bl_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        bl_btn.clicked.connect(self.open_settings)
        bl.addWidget(bl_text, 1)
        bl.addWidget(bl_btn)
        banner_wrap = QWidget()
        bw = QVBoxLayout(banner_wrap)
        bw.setContentsMargins(20, 10, 20, 0)
        bw.addWidget(self.banner)
        self.banner_wrap = banner_wrap
        mv.addWidget(banner_wrap)

        # повідомлення
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        host = QWidget()
        host.setObjectName("chatHost")
        self.msg_layout = QVBoxLayout(host)
        self.msg_layout.setContentsMargins(14, 12, 14, 12)
        self.msg_layout.setSpacing(2)
        self.msg_layout.addStretch(1)
        self.scroll.setWidget(host)
        mv.addWidget(self.scroll, 1)

        # індикатор і статус
        self.typing = QLabel("APEXUS думає")
        self.typing.setObjectName("typing")
        self.typing.hide()
        self.typing_timer = QTimer(self)
        self.typing_timer.setInterval(380)
        self.typing_timer.timeout.connect(self._tick_typing)
        mv.addWidget(self.typing)

        self.status = QLabel("")
        self.status.setObjectName("status")
        self.status.hide()
        self.status_timer = QTimer(self)
        self.status_timer.setSingleShot(True)
        self.status_timer.timeout.connect(self.status.hide)
        mv.addWidget(self.status)

        # поле введення
        bar = QWidget()
        bv = QVBoxLayout(bar)
        bv.setContentsMargins(20, 6, 20, 18)
        frame = QFrame()
        frame.setObjectName("inputFrame")
        fl = QHBoxLayout(frame)
        fl.setContentsMargins(14, 6, 8, 6)
        fl.setSpacing(8)
        self.input = InputBox()
        self.input.submit.connect(self.on_send)
        self.send_btn = QPushButton("Надіслати  ➤")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.send_btn.clicked.connect(self.on_send)
        fl.addWidget(self.input, 1)
        fl.addWidget(self.send_btn, 0, Qt.AlignmentFlag.AlignBottom)
        bv.addWidget(frame)
        mv.addWidget(bar)

        outer.addWidget(main, 1)

    def apply_style(self) -> None:
        font = QFont("Segoe UI")
        font.setPixelSize(self.settings.font_size)
        QApplication.setFont(font)
        self.setStyleSheet(STYLE)
        self.subtitle.setText(
            f"Ваш AI-помічник   •   {provider_name(self.settings.api_url)}   •   модель: {self.settings.model}"
        )
        if self.settings.animations:
            if self.glow_anim.state() != QPropertyAnimation.State.Running:
                self.glow_anim.start()
        else:
            self.glow_anim.stop()
            self.glow.setBlurRadius(30)

    def update_banner(self) -> None:
        self.banner_wrap.setVisible(self.settings.needs_key())

    # ------------------------------------------------------------ повідомлення
    def _clear_messages(self) -> None:
        for row in self.rows:
            row.deleteLater()
        self.rows = []
        if self.welcome is not None:
            self.welcome.deleteLater()
            self.welcome = None

    def _show_welcome(self) -> None:
        self.welcome = QLabel(
            "<div style='text-align:center'>"
            "<p style='font-size:26px; font-weight:700; color:#e6e8f2'>Привіт! Я APEXUS 👋</p>"
            "<p style='font-size:15px'>Запитайте мене про що завгодно — код, тексти, ідеї чи навчання.</p>"
            "</div>"
        )
        self.welcome.setObjectName("welcome")
        self.welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome.setTextFormat(Qt.TextFormat.RichText)
        self.msg_layout.insertWidget(0, self.welcome)
        self.msg_layout.insertSpacing(0, 90)

    def _bubble_width(self) -> int:
        return max(280, int(self.scroll.viewport().width() * 0.78))

    def _add_row(self, role: str, text: str, animate: bool = True) -> None:
        if self.welcome is not None:
            self.welcome.deleteLater()
            self.welcome = None
            # прибираємо розпірку, додану разом із вітанням
            item = self.msg_layout.itemAt(0)
            if item is not None and item.spacerItem() is not None and item.widget() is None:
                self.msg_layout.takeAt(0)
        row = MessageRow(role, text)
        row.set_max_width(self._bubble_width())
        self.rows.append(row)
        self.msg_layout.insertWidget(self.msg_layout.count() - 1, row)
        if animate and self.settings.animations:
            effect = QGraphicsOpacityEffect(row)
            row.setGraphicsEffect(effect)
            anim = QPropertyAnimation(effect, b"opacity", row)
            anim.setDuration(300)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.finished.connect(partial(row.setGraphicsEffect, None))
            row._anim = anim
            anim.start()
        self._scroll_bottom()

    def _scroll_bottom(self) -> None:
        def go() -> None:
            bar = self.scroll.verticalScrollBar()
            bar.setValue(bar.maximum())

        QTimer.singleShot(30, go)
        QTimer.singleShot(250, go)

    def render_chat(self) -> None:
        self._clear_messages()
        # повністю очищаємо layout від зайвих розпорок, залишаючи лише хвостовий stretch
        while self.msg_layout.count() > 0:
            item = self.msg_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self.msg_layout.addStretch(1)

        chat = self.store.get(self.current_id)
        if chat is None or not chat.messages:
            self._show_welcome()
        else:
            for m in chat.messages:
                self._add_row(m.role, m.content, animate=False)
        self._update_typing_visibility()
        self._scroll_bottom()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        width = self._bubble_width()
        for row in self.rows:
            row.set_max_width(width)

    # ----------------------------------------------------------------- чати
    def refresh_list(self) -> None:
        self._updating_list = True
        self.list.clear()
        for chat in self.store.sorted_chats():
            item = QListWidgetItem(chat.title)
            item.setData(Qt.ItemDataRole.UserRole, chat.id)
            item.setToolTip(chat.title)
            self.list.addItem(item)
            if chat.id == self.current_id:
                self.list.setCurrentItem(item)
        self._updating_list = False

    def _on_item_changed(self, current, _previous) -> None:
        if self._updating_list or current is None:
            return
        chat_id = current.data(Qt.ItemDataRole.UserRole)
        if chat_id != self.current_id:
            self.open_chat(chat_id)

    def open_chat(self, chat_id: str) -> None:
        self.current_id = chat_id
        self.render_chat()
        self.refresh_list()
        self.input.setFocus()

    def new_chat(self) -> None:
        current = self.store.get(self.current_id)
        if current is not None and not current.messages:
            self.input.setFocus()
            return
        chat = self.store.new_chat()
        self.current_id = chat.id
        self.render_chat()
        self.refresh_list()
        self.input.setFocus()

    def _list_menu(self, pos) -> None:
        item = self.list.itemAt(pos)
        if item is None:
            return
        chat_id = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        rename = menu.addAction("Перейменувати")
        delete = menu.addAction("Видалити")
        chosen = menu.exec(self.list.viewport().mapToGlobal(pos))
        if chosen is rename:
            self._rename_chat(chat_id)
        elif chosen is delete:
            self._delete_chat(chat_id)

    def _rename_chat(self, chat_id: str) -> None:
        chat = self.store.get(chat_id)
        if chat is None:
            return
        dlg = QInputDialog(self)
        dlg.setWindowTitle("Перейменувати чат")
        dlg.setLabelText("Нова назва чату:")
        dlg.setTextValue(chat.title)
        dlg.setOkButtonText("Зберегти")
        dlg.setCancelButtonText("Скасувати")
        if dlg.exec():
            self.store.rename(chat_id, dlg.textValue())
            self.refresh_list()

    def _delete_chat(self, chat_id: str) -> None:
        if not self._confirm("Видалити цей чат назавжди?"):
            return
        self.store.delete(chat_id)
        if chat_id == self.current_id:
            self.current_id = None
            chats = self.store.sorted_chats()
            if chats:
                self.open_chat(chats[0].id)
            else:
                self.new_chat()
        else:
            self.refresh_list()

    def clear_history(self) -> None:
        if not self._confirm("Видалити всю історію чатів? Цю дію неможливо скасувати."):
            return
        self.store.clear_all()
        self.current_id = None
        self.new_chat()

    def _confirm(self, text: str) -> bool:
        box = QMessageBox(self)
        box.setWindowTitle("APEXUS 1V")
        box.setIcon(QMessageBox.Icon.Question)
        box.setText(text)
        yes = box.addButton("Так", QMessageBox.ButtonRole.AcceptRole)
        box.addButton("Скасувати", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        return box.clickedButton() is yes

    # --------------------------------------------------------- відправлення
    def flash_status(self, text: str, ms: int = 3500) -> None:
        self.status.setText(text)
        self.status.show()
        self.status_timer.start(ms)

    def on_send(self) -> None:
        text = self.input.toPlainText().strip()
        if not text:
            self.flash_status("Введіть повідомлення перед відправленням.")
            return
        if self.busy:
            self.flash_status("Зачекайте, APEXUS ще відповідає…")
            return
        if self.settings.needs_key():
            self.update_banner()
            self._add_row(
                "error",
                "API-ключ не знайдено.\n\n"
                "Відкрийте «Налаштування», оберіть сервіс і введіть ключ "
                "(або задайте змінну середовища DEEPSEEK_API_KEY і перезапустіть застосунок).",
            )
            return

        chat = self.store.get(self.current_id)
        if chat is None:
            self.new_chat()
            chat = self.store.get(self.current_id)
        self.store.add_message(chat, "user", text)
        self.input.clear()
        self._add_row("user", text)
        self.refresh_list()

        self.busy = True
        self.busy_chat_id = chat.id
        self.send_btn.setEnabled(False)
        self._update_typing_visibility()

        worker = ChatWorker(chat.id, dataclasses.replace(self.settings), list(chat.messages))
        worker.succeeded.connect(self._on_reply)
        worker.failed.connect(self._on_failure)
        worker.finished.connect(partial(self._worker_done, worker))
        self._workers.append(worker)
        worker.start()

    def _worker_done(self, worker: ChatWorker) -> None:
        if worker in self._workers:
            self._workers.remove(worker)
        worker.deleteLater()

    def _finish_busy(self) -> None:
        self.busy = False
        self.busy_chat_id = None
        self.send_btn.setEnabled(True)
        self._update_typing_visibility()

    def _on_reply(self, chat_id: str, text: str) -> None:
        self._finish_busy()
        chat = self.store.get(chat_id)
        if chat is None:
            return
        self.store.add_message(chat, "assistant", text)
        if chat_id == self.current_id:
            self._add_row("assistant", text)
        else:
            self.flash_status(f"Нова відповідь у чаті «{chat.title}».")
        self.refresh_list()

    def _on_failure(self, chat_id: str, message: str) -> None:
        self._finish_busy()
        if chat_id == self.current_id:
            self._add_row("error", message)
        else:
            self.flash_status(message)

    # ------------------------------------------------------ індикатор «думає»
    def _update_typing_visibility(self) -> None:
        show = self.busy and self.busy_chat_id == self.current_id
        self.typing.setVisible(show)
        if show:
            self._dots = 0
            self._tick_typing()
            self.typing_timer.start()
        else:
            self.typing_timer.stop()

    def _tick_typing(self) -> None:
        self._dots = (self._dots % 3) + 1
        self.typing.setText("APEXUS думає" + "." * self._dots)

    # ---------------------------------------------------------- налаштування
    def open_settings(self) -> None:
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec():
            self.settings = dlg.result_settings()
            self.settings.save()
            self.apply_style()
            self.update_banner()
            self.render_chat()
            self.flash_status("Налаштування збережено.")

    def closeEvent(self, event) -> None:
        for worker in list(self._workers):
            if worker.isRunning() and not worker.wait(300):
                worker.terminate()
                worker.wait(500)
        self.store.save()
        super().closeEvent(event)
