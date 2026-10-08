"""
CODER-OS Setup Wizard
Interactive onboarding and software selector for CODER-OS.
Supports both Live ISO pre-installation and Post-install customization.
"""

import sys
import os
import json
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QRadioButton, QButtonGroup, QCheckBox,
    QStackedWidget, QScrollArea, QFrame, QGridLayout, QProgressBar,
    QMessageBox, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPalette, QIcon, QPainter, QLinearGradient

PROFILES = {
    "hardcore": {
        "title": "Хардкорный Кодер (Hardcore CLI)",
        "icon": "⚡",
        "badge": "TERMINAL FIRST",
        "description": "Максимум производительности, минимум GUI. Только терминал, Neovim, Rust, C++, Go, Tmux, Docker и горячие клавиши.",
        "packages": [
            "neovim", "tmux", "zsh", "starship", "kitty", "rustup", "go",
            "gcc", "clang", "cmake", "ninja", "docker", "docker-compose",
            "ripgrep", "fzf", "lazygit", "lazydocker", "btop", "eza", "bat", "fastfetch"
        ],
        "default_shell": "zsh",
        "desktop": "hyprland"
    },
    "vibe": {
        "title": "Вайб-Кодер (AI & Fast Prototyping)",
        "icon": "🤖",
        "badge": "AI & MODERN DEV",
        "description": "Быстрый прототипинг, нейросети и современный стек. VS Code, Python + uv, Node.js + Bun, Ollama для локальных LLM, Docker, Postman.",
        "packages": [
            "code", "python", "python-pip", "uv", "nodejs", "bun", "pnpm",
            "ollama", "docker", "docker-compose", "kitty", "zsh", "starship",
            "firefox", "bruno", "lazygit", "fastfetch", "btop"
        ],
        "default_shell": "zsh",
        "desktop": "hyprland"
    },
    "linux_lover": {
        "title": "Линуксоид из коробки (Full Experience)",
        "icon": "🐧",
        "badge": "OUT OF THE BOX",
        "description": "Полноценная система для жизни и работы со всеми удобствами: браузер, мессенджеры, медиа, плоская интеграция Flatpak, красивый UI.",
        "packages": [
            "code", "firefox", "telegram-desktop", "discord", "vlc",
            "flatpak", "zsh", "starship", "kitty", "btop", "fastfetch",
            "libreoffice-fresh", "python", "nodejs", "git"
        ],
        "default_shell": "zsh",
        "desktop": "kde"
    },
    "custom": {
        "title": "Кастомный выбор (Custom Build)",
        "icon": "🛠️",
        "badge": "FULL CONTROL",
        "description": "Тонкая ручная настройка: выбери каждую утилиту, язык, редактор и графическое окружение самостоятельно.",
        "packages": [],
        "default_shell": "zsh",
        "desktop": "hyprland"
    }
}

CATEGORIES = [
    {
        "id": "editors",
        "name": "💻 Редакторы и IDE",
        "desc": "Среда разработки на любой вкус",
        "items": [
            ("code", "Visual Studio Code", "Популярный расширяемый редактор с поддержкой AI плагинов", True),
            ("vscodium", "VSCodium", "Полностью открытая версия VS Code без телеметрии Microsoft", False),
            ("neovim", "Neovim + LazyVim", "Молниеносный терминальный редактор с плагинами и LSP", True),
            ("zed", "Zed Editor", "Сверхбыстрый редактор на Rust для командной работы", False),
            ("helix", "Helix Editor", "Пост-современный модальный редактор с Kakoune-подобным управлением", False),
            ("sublime-text", "Sublime Text 4", "Легендарный быстрый редактор кода", False)
        ]
    },
    {
        "id": "languages",
        "name": "⚡ Языки и Среды Исполнения",
        "desc": "Компиляторы, интерпретаторы и менеджеры пакетов",
        "items": [
            ("python", "Python 3 + uv / pip", "Современный Python с быстрым менеджером пакетов uv", True),
            ("nodejs", "Node.js (LTS) + npm", "JavaScript рантайм для бэкенда и веб-разработки", True),
            ("bun", "Bun & pnpm", "Сверхбыстрый JS/TS рантайм и пакетный менеджер", True),
            ("rustup", "Rust Toolchain (rustup + cargo)", "Язык Rust для системного программирования", True),
            ("go", "Go (Golang)", "Простой и высокопроизводительный язык от Google", False),
            ("gcc-clang", "C/C++ (GCC, Clang, CMake, Ninja)", "Полный набор для нативной разработки на C и C++", True),
            ("jdk", "OpenJDK 21 (Java)", "Среда разработки Java для энтерпрайза и Android", False)
        ]
    },
    {
        "id": "ai_tools",
        "name": "🧠 AI и Вайб-Инструменты",
        "desc": "Локальные нейросети и ассистенты для ускорения разработки",
        "items": [
            ("ollama", "Ollama (Локальные LLM)", "Запуск Llama 3, DeepSeek, Qwen и Mistral прямо на твоём GPU/CPU", True),
            ("aider", "Aider AI Pair Programmer", "AI помощник прямо в терминале с доступом к Git", True),
            ("shell-gpt", "Shell-GPT (sgpt)", "Генерация bash-скриптов и команд через LLM прямо в консоли", False)
        ]
    },
    {
        "id": "devops",
        "name": "🐳 DevOps и Контейнеры",
        "desc": "Виртуализация, контейнеризация и оркестрация",
        "items": [
            ("docker", "Docker & Docker Compose", "Стандарт индустрии для контейнеризации приложений", True),
            ("podman", "Podman & Podman Compose", "Rootless альтернатива Docker от Red Hat", False),
            ("k8s", "Kubernetes Tools (kubectl, k9s, helm)", "Инструменты управления K8s кластерами", False),
            ("minikube", "Minikube", "Локальный кластер Kubernetes для разработки", False)
        ]
    },
    {
        "id": "terminal",
        "name": "🚀 Терминал и CLI Утилиты",
        "desc": "Инструменты для продуктивности и эстетики в консоли",
        "items": [
            ("kitty", "Kitty Terminal (GPU-accelerated)", "Быстрый терминал с рендерингом на видеокарте", True),
            ("alacritty", "Alacritty", "Минималистичный терминал на Rust", False),
            ("starship", "Starship Cross-shell Prompt", "Умный и информативный промпт для Zsh/Fish/Bash", True),
            ("zsh-suite", "Zsh + Автодополнение + Подсветка", "zsh-autosuggestions, syntax-highlighting", True),
            ("fish", "Fish Shell", "Интуитивная оболочка с умным автодополнением из коробки", False),
            ("cli-essentials", "CLI Pack (ripgrep, fzf, bat, eza)", "Современная замена grep, find, cat, ls", True),
            ("git-tools", "Lazygit & Lazydocker", "Превосходные TUI интерфейсы для Git и Docker", True),
            ("monitoring", "Btop & Fastfetch", "Красивый системный монитор и системное инфо", True)
        ]
    },
    {
        "id": "browsers_tools",
        "name": "🌐 Браузеры, Базы и Инструменты",
        "desc": "Инструменты для тестирования API, баз данных и веба",
        "items": [
            ("firefox", "Firefox Developer / Standard", "Быстрый и защищённый веб-браузер", True),
            ("brave", "Brave Browser", "Браузер на базе Chromium со встроенным блокировщиком", False),
            ("bruno", "Bruno (API Client)", "Легковесный Git-friendly клиент для REST/GraphQL API (замена Postman)", True),
            ("dbeaver", "DBeaver Universal SQL Client", "Универсальный GUI менеджер для PostgreSQL, MySQL, SQLite", False),
            ("redis-tools", "Redis Tools & CLI", "Клиенты для работы с Redis и key-value хранилищами", False)
        ]
    },
    {
        "id": "gui_apps",
        "name": "💬 Мессенджеры и Мультимедиа",
        "desc": "Связь, документация и развлечения",
        "items": [
            ("telegram", "Telegram Desktop", "Быстрый официальный клиент Telegram", True),
            ("discord", "Discord / WebCord", "Голосовое и текстовое общение для разработчиков", False),
            ("obsidian", "Obsidian Markdown Notes", "База знаний и заметки для ведения документации проектов", True),
            ("vlc", "VLC Media Player", "Всеядный медиаплеер", True),
            ("libreoffice", "LibreOffice Fresh", "Пакет офисных программ (таблицы, документы)", False)
        ]
    }
]

STYLESHEET = """
QMainWindow {
    background-color: #0b0f19;
}
QWidget {
    color: #e2e8f0;
    font-family: 'Segoe UI', 'Ubuntu', 'Inter', sans-serif;
}
QFrame#Card {
    background-color: #131b2e;
    border: 1px solid #1e293b;
    border-radius: 12px;
}
QFrame#Card:hover {
    border: 1px solid #38bdf8;
    background-color: #17223b;
}
QFrame#SelectedCard {
    background-color: #111e38;
    border: 2px solid #38bdf8;
    border-radius: 12px;
}
QLabel#HeaderTitle {
    font-size: 26px;
    font-weight: 800;
    color: #f8fafc;
}
QLabel#HeaderSubtitle {
    font-size: 14px;
    color: #94a3b8;
}
QLabel#CardTitle {
    font-size: 16px;
    font-weight: 700;
    color: #38bdf8;
}
QLabel#CardDesc {
    font-size: 13px;
    color: #94a3b8;
}
QLabel#Badge {
    background-color: #0284c7;
    color: #ffffff;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
}
QPushButton#PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    color: #0f172a;
    font-size: 15px;
    font-weight: 700;
    padding: 12px 28px;
    border-radius: 8px;
    border: none;
}
QPushButton#PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369a1, stop:1 #0ea5e9);
    color: #ffffff;
}
QPushButton#SecondaryBtn {
    background-color: #1e293b;
    color: #cbd5e1;
    font-size: 14px;
    font-weight: 600;
    padding: 12px 24px;
    border-radius: 8px;
    border: 1px solid #334155;
}
QPushButton#SecondaryBtn:hover {
    background-color: #334155;
    color: #f8fafc;
}
QCheckBox {
    font-size: 14px;
    font-weight: 600;
    color: #f1f5f9;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 5px;
    border: 1px solid #475569;
    background-color: #0f172a;
}
QCheckBox::indicator:checked {
    background-color: #0284c7;
    border: 1px solid #38bdf8;
}
QScrollArea {
    border: none;
    background-color: transparent;
}
QScrollBar:vertical {
    border: none;
    background: #0f172a;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #334155;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background: #475569;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QLineEdit, QComboBox {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 10px 14px;
    color: #f8fafc;
    font-size: 14px;
}
QLineEdit:focus, QComboBox:focus {
    border: 1px solid #38bdf8;
}
"""


class ProfileCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, profile_id, data, parent=None):
        super().__init__(parent)
        self.profile_id = profile_id
        self.setObjectName("Card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_selected = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        # Header with icon and badge
        top_layout = QHBoxLayout()
        icon_label = QLabel(data["icon"])
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        top_layout.addWidget(icon_label)

        top_layout.addStretch()

        badge_label = QLabel(data["badge"])
        badge_label.setObjectName("Badge")
        top_layout.addWidget(badge_label)
        layout.addLayout(top_layout)

        # Title
        title_label = QLabel(data["title"])
        title_label.setObjectName("CardTitle")
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(data["description"])
        desc_label.setObjectName("CardDesc")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        layout.addStretch()

    def set_selected(self, selected):
        self.is_selected = selected
        self.setObjectName("SelectedCard" if selected else "Card")
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        self.clicked.emit(self.profile_id)
        super().mousePressEvent(event)


class CoderWizard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CODER-OS • Мастер Начальной Настройки")
        self.setMinimumSize(1000, 720)
        self.resize(1080, 760)
        self.setStyleSheet(STYLESHEET)

        self.selected_profile = "vibe"
        self.package_checkboxes = {}
        self.profile_cards = {}

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(36, 28, 36, 28)
        self.main_layout.setSpacing(20)

        self.init_header()
        self.init_stack()
        self.init_footer()

        # Set default selection
        self.on_profile_selected("vibe")

    def init_header(self):
        header_layout = QHBoxLayout()
        
        logo_box = QVBoxLayout()
        title = QLabel("CODER-OS 🚀")
        title.setObjectName("HeaderTitle")
        subtitle = QLabel("Дистрибутив для настоящих разработчиков и вайб-кодеров на базе Arch Linux")
        subtitle.setObjectName("HeaderSubtitle")
        logo_box.addWidget(title)
        logo_box.addWidget(subtitle)
        header_layout.addLayout(logo_box)

        header_layout.addStretch()

        # Step indicator
        self.step_label = QLabel("ШАГ 1 ИЗ 3")
        self.step_label.setObjectName("Badge")
        self.step_label.setStyleSheet("background-color: #1e293b; color: #38bdf8; font-size: 12px; padding: 6px 14px; border: 1px solid #38bdf8;")
        header_layout.addWidget(self.step_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.main_layout.addLayout(header_layout)

    def init_stack(self):
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.page1_profile = self.create_page_profile()
        self.page2_packages = self.create_page_packages()
        self.page3_summary = self.create_page_summary()

        self.stack.addWidget(self.page1_profile)
        self.stack.addWidget(self.page2_packages)
        self.stack.addWidget(self.page3_summary)

    def create_page_profile(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(20)

        prompt = QLabel("КТО ТЫ? ВЫБЕРИ СВОЙ СТИЛЬ КОДИНГА")
        prompt.setStyleSheet("font-size: 18px; font-weight: 700; color: #f8fafc; letter-spacing: 1px;")
        layout.addWidget(prompt)

        hint = QLabel("Мы автоматически подберем идеальный набор инструментов, оболочку и окружение.")
        hint.setStyleSheet("font-size: 14px; color: #94a3b8;")
        layout.addWidget(hint)

        # 2x2 Grid of Profile Cards
        grid = QGridLayout()
        grid.setSpacing(18)

        card_keys = list(PROFILES.keys())
        for idx, key in enumerate(card_keys):
            card = ProfileCard(key, PROFILES[key])
            card.clicked.connect(self.on_profile_selected)
            self.profile_cards[key] = card
            row = idx // 2
            col = idx % 2
            grid.addWidget(card, row, col)

        layout.addLayout(grid)
        layout.addStretch()
        return page

    def create_page_packages(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(15)

        top_info = QHBoxLayout()
        header = QLabel("ВЫБОР ПРОГРАММ И ИНСТРУМЕНТОВ")
        header.setStyleSheet("font-size: 18px; font-weight: 700; color: #f8fafc;")
        top_info.addWidget(header)
        top_info.addStretch()

        self.selection_count_label = QLabel("Выбрано пакетов: 0")
        self.selection_count_label.setStyleSheet("color: #38bdf8; font-weight: 600; font-size: 14px;")
        top_info.addWidget(self.selection_count_label)
        layout.addLayout(top_info)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(24)

        for cat in CATEGORIES:
            cat_box = QFrame()
            cat_box.setStyleSheet("background-color: #131b2e; border: 1px solid #1e293b; border-radius: 10px; padding: 14px;")
            cat_layout = QVBoxLayout(cat_box)
            cat_layout.setSpacing(12)

            cat_title = QLabel(cat["name"])
            cat_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #38bdf8; border: none; padding: 0;")
            cat_desc = QLabel(cat["desc"])
            cat_desc.setStyleSheet("font-size: 12px; color: #64748b; border: none; padding: 0;")

            cat_layout.addWidget(cat_title)
            cat_layout.addWidget(cat_desc)

            items_grid = QGridLayout()
            items_grid.setSpacing(10)
            items_grid.setContentsMargins(0, 6, 0, 0)

            for item_idx, (pkg_id, name, desc, default_val) in enumerate(cat["items"]):
                item_widget = QWidget()
                item_widget.setStyleSheet("border: none;")
                item_v = QVBoxLayout(item_widget)
                item_v.setContentsMargins(4, 4, 4, 4)
                item_v.setSpacing(3)

                cb = QCheckBox(name)
                cb.setChecked(default_val)
                cb.stateChanged.connect(self.update_package_count)
                self.package_checkboxes[pkg_id] = cb

                lbl_desc = QLabel(desc)
                lbl_desc.setStyleSheet("color: #94a3b8; font-size: 11px; margin-left: 28px;")
                lbl_desc.setWordWrap(True)

                item_v.addWidget(cb)
                item_v.addWidget(lbl_desc)

                r = item_idx // 2
                c = item_idx % 2
                items_grid.addWidget(item_widget, r, c)

            cat_layout.addLayout(items_grid)
            scroll_layout.addWidget(cat_box)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        return page

    def create_page_summary(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 10)
        layout.setSpacing(18)

        header = QLabel("ИТОГОВАЯ КОНФИГУРАЦИЯ СИСТЕМЫ")
        header.setStyleSheet("font-size: 18px; font-weight: 700; color: #f8fafc;")
        layout.addWidget(header)

        # Settings Card
        settings_box = QFrame()
        settings_box.setStyleSheet("background-color: #131b2e; border: 1px solid #1e293b; border-radius: 12px; padding: 16px;")
        s_layout = QGridLayout(settings_box)
        s_layout.setSpacing(16)

        # User and Host
        s_layout.addWidget(QLabel("Имя пользователя (User):"), 0, 0)
        self.username_input = QLineEdit("coder")
        s_layout.addWidget(self.username_input, 0, 1)

        s_layout.addWidget(QLabel("Имя компьютера (Hostname):"), 1, 0)
        self.hostname_input = QLineEdit("coder-os")
        s_layout.addWidget(self.hostname_input, 1, 1)

        # Shell
        s_layout.addWidget(QLabel("Основная оболочка (Shell):"), 2, 0)
        self.shell_combo = QComboBox()
        self.shell_combo.addItems(["zsh (Zsh + Starship + Plugins)", "fish (Friendly Interactive Shell)", "bash"])
        s_layout.addWidget(self.shell_combo, 2, 1)

        # Desktop Environment
        s_layout.addWidget(QLabel("Графическое окружение:"), 3, 0)
        self.de_combo = QComboBox()
        self.de_combo.addItems([
            "Hyprland (Cyber Coder Rice - Wayland, ультрабыстрый)",
            "KDE Plasma 6 (Современный, настраиваемый, надёжный)",
            "CLI Minimal (Только терминал без графики)"
        ])
        s_layout.addWidget(self.de_combo, 3, 1)

        layout.addWidget(settings_box)

        # Summary box
        summary_card = QFrame()
        summary_card.setStyleSheet("background-color: #0f172a; border: 1px solid #334155; border-radius: 12px; padding: 18px;")
        sum_layout = QVBoxLayout(summary_card)

        sum_title = QLabel("Готовность к развертыванию")
        sum_title.setStyleSheet("font-size: 16px; font-weight: 700; color: #38bdf8;")
        sum_layout.addWidget(sum_title)

        self.summary_text = QLabel()
        self.summary_text.setStyleSheet("font-size: 14px; color: #cbd5e1; line-height: 150%;")
        self.summary_text.setWordWrap(True)
        sum_layout.addWidget(self.summary_text)

        layout.addWidget(summary_card)
        layout.addStretch()
        return page

    def init_footer(self):
        footer_layout = QHBoxLayout()

        self.back_btn = QPushButton("← Назад")
        self.back_btn.setObjectName("SecondaryBtn")
        self.back_btn.setEnabled(False)
        self.back_btn.clicked.connect(self.go_back)
        footer_layout.addWidget(self.back_btn)

        footer_layout.addStretch()

        self.next_btn = QPushButton("Продолжить →")
        self.next_btn.setObjectName("PrimaryBtn")
        self.next_btn.clicked.connect(self.go_next)
        footer_layout.addWidget(self.next_btn)

        self.main_layout.addLayout(footer_layout)

    def on_profile_selected(self, profile_id):
        self.selected_profile = profile_id
        for p_id, card in self.profile_cards.items():
            card.set_selected(p_id == profile_id)

        # Apply profile defaults to packages
        profile_data = PROFILES[profile_id]
        if profile_id != "custom":
            preset_pkgs = profile_data["packages"]
            for pkg_id, cb in self.package_checkboxes.items():
                cb.setChecked(pkg_id in preset_pkgs or any(p in pkg_id for p in preset_pkgs))

        self.update_package_count()

    def update_package_count(self):
        selected_count = sum(1 for cb in self.package_checkboxes.values() if cb.isChecked())
        if hasattr(self, 'selection_count_label'):
            self.selection_count_label.setText(f"Выбрано пакетов: {selected_count}")

    def update_summary_page(self):
        selected_pkgs = [cb.text() for cb in self.package_checkboxes.values() if cb.isChecked()]
        profile_name = PROFILES[self.selected_profile]["title"]
        desktop_choice = self.de_combo.currentText()
        shell_choice = self.shell_combo.currentText().split()[0]
        user = self.username_input.text() or "coder"
        host = self.hostname_input.text() or "coder-os"

        summary = (
            f"<b>Выбранный профиль:</b> {profile_name}<br>"
            f"<b>Пользователь:</b> {user}@{host}<br>"
            f"<b>Оболочка:</b> {shell_choice}<br>"
            f"<b>Окружение:</b> {desktop_choice}<br>"
            f"<b>Количество выбранных инструментов:</b> {len(selected_pkgs)} шт.<br><br>"
            f"<i>При нажатии «Начать установку» сгенерируется манифест конфигурации "
            f"и запустится установщик Calamares с преднастроенными модулями.</i>"
        )
        self.summary_text.setText(summary)

    def go_next(self):
        curr = self.stack.currentIndex()
        if curr == 0:
            self.stack.setCurrentIndex(1)
            self.step_label.setText("ШАГ 2 ИЗ 3")
            self.back_btn.setEnabled(True)
        elif curr == 1:
            self.update_summary_page()
            self.stack.setCurrentIndex(2)
            self.step_label.setText("ШАГ 3 ИЗ 3")
            self.next_btn.setText("🚀 Начать установку")
        elif curr == 2:
            self.save_and_launch_install()

    def go_back(self):
        curr = self.stack.currentIndex()
        if curr == 2:
            self.stack.setCurrentIndex(1)
            self.step_label.setText("ШАГ 2 ИЗ 3")
            self.next_btn.setText("Продолжить →")
        elif curr == 1:
            self.stack.setCurrentIndex(0)
            self.step_label.setText("ШАГ 1 ИЗ 3")
            self.back_btn.setEnabled(False)

    def save_and_launch_install(self):
        manifest = {
            "os_name": "CODER-OS",
            "version": "1.0.0-alpha",
            "profile": self.selected_profile,
            "username": self.username_input.text().strip() or "coder",
            "hostname": self.hostname_input.text().strip() or "coder-os",
            "shell": self.shell_combo.currentText().split()[0],
            "desktop": self.de_combo.currentText(),
            "selected_packages": [pkg_id for pkg_id, cb in self.package_checkboxes.items() if cb.isChecked()]
        }

        # Save manifest
        manifest_dir = "/etc/coder-os" if os.path.exists("/etc") else os.path.abspath(".")
        os.makedirs(manifest_dir, exist_ok=True)
        manifest_path = os.path.join(manifest_dir, "coder-manifest.json")
        try:
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Manifest save warning: {e}")

        # Check if running in Live ISO environment with Calamares
        if os.path.exists("/usr/bin/calamares"):
            QMessageBox.information(
                self,
                "CODER-OS",
                f"Конфигурация сохранена в {manifest_path}!\nЗапуск графического установщика Calamares..."
            )
            subprocess.Popen(["pkexec", "calamares"])
            self.close()
        else:
            QMessageBox.information(
                self,
                "CODER-OS • Конфигурация готова!",
                f"Манифест успешно создан:\n{manifest_path}\n\n"
                f"В установленной системе или на Live-флешке этот манифест передаётся в установщик "
                f"для автоматического развертывания выбранного окружения и пакетов."
            )


def main():
    app = QApplication(sys.argv)
    wizard = CoderWizard()
    wizard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
