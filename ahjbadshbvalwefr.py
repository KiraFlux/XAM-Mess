import time
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
from PIL import Image, ImageTk


class XAMMessenger:
    def __init__(self, root):
        self.root = root
        self.root.title("XAM Messenger")
        self.root.geometry("1200x800")
        self.root.configure(bg="#182533")
        self.root.minsize(1200, 800)

        # Загрузка аватарки
        try:
            self.avatar_image = Image.open("icon.jpg")
            self.avatar_image = self.avatar_image.resize((40, 40), Image.LANCZOS)
            self.avatar_photo = ImageTk.PhotoImage(self.avatar_image)
        except FileNotFoundError:
            self.avatar_photo = None

        # Стили
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#182533")
        self.style.configure("TLabel", background="#182533", foreground="white")
        self.style.configure("TButton", background="#182533", foreground="white", borderwidth=0)
        self.style.configure("TEntry", fieldbackground="#2A3B4C", foreground="white", font=("Segoe UI", 11))
        self.style.map("TButton", background=[("active", "#2A3B4C")])

        # Данные приложения
        self.contacts = {
            "Максим": [],
            "Анна": [("Анна", "Привет! Как дела?"), ("Я", "Привет! Всё отлично!")],
            "Борис": [("Борис", "Ты посмотрел документы?"), ("Я", "Да, я их уже отправил.")],
            "Виктор": [("Виктор", "Напомни, когда у нас встреча?"), ("Я", "В среду в 14:00")],
            "Дарья": [("Дарья", "Скинула тебе файл"), ("Я", "Получил, спасибо!")],
            "Евгений": [("Евгений", "Готов к завтрашней презентации?"), ("Я", "Да, всё готово!")],
            "Зоя": [("Зоя", "Как прошла поездка?"), ("Я", "Очень хорошо, спасибо!")]
        }
        self.current_chat = "Максим"

        # Основные разделы интерфейса
        self.create_left_sidebar()
        self.create_chat_area()
        self.create_message_input()

        # Загрузка данных
        self.load_contacts()
        self.contact_list.selection_set(0)
        self.switch_chat()

    def create_left_sidebar(self):
        # Панель контактов
        self.left_frame = ttk.Frame(self.root, width=250)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.left_frame.pack_propagate(False)

        # Заголовок
        header = ttk.Frame(self.left_frame)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Чаты", font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=10)

        # Поиск
        search_frame = ttk.Frame(self.left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=23)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, padx=(0, 5), expand=True)
        self.search_entry.insert(0, "Поиск...")
        self.search_entry.bind("<FocusIn>", lambda e: self.search_entry.delete(0, tk.END))
        self.search_entry.bind("<KeyRelease>", self.filter_contacts)

        search_btn = ttk.Button(search_frame, text="🔍", width=3)
        search_btn.pack(side=tk.RIGHT)

        # Список контактов
        self.contact_list = tk.Listbox(
            self.left_frame,
            bg="#2A3B4C",
            fg="white",
            borderwidth=0,
            highlightthickness=0,
            selectbackground="#3d5466",
            activestyle="none",
            font=("Segoe UI", 11),
            selectmode=tk.SINGLE
        )
        self.contact_list.pack(fill=tk.BOTH, expand=True)
        self.contact_list.bind("<<ListboxSelect>>", self.switch_chat)

        # Нижняя панель
        bottom_frame = ttk.Frame(self.left_frame)
        bottom_frame.pack(fill=tk.X, pady=(5, 0))

        new_chat_btn = ttk.Button(
            bottom_frame,
            text="Новый чат",
            command=self.create_new_chat,
            width=10
        )
        new_chat_btn.pack(side=tk.LEFT, padx=2)

        settings_btn = ttk.Button(bottom_frame, text="Настройки", width=10)
        settings_btn.pack(side=tk.RIGHT, padx=2)

    def create_chat_area(self):
        # Область чата
        main_frame = ttk.Frame(self.root)
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5), pady=5)

        # Заголовок чата
        self.header_frame = ttk.Frame(main_frame, height=60)
        self.header_frame.pack(fill=tk.X)
        self.header_frame.pack_propagate(False)

        # Аватарка
        self.avatar_label = ttk.Label(self.header_frame)
        self.avatar_label.pack(side=tk.LEFT, padx=(10, 5))

        # Имя чата и кнопки
        info_frame = ttk.Frame(self.header_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.chat_title = ttk.Label(
            info_frame,
            text=self.current_chat,
            font=("Segoe UI", 12, "bold")
        )
        self.chat_title.pack(anchor=tk.W, padx=(0, 10))

        status_label = ttk.Label(
            info_frame,
            text="в сети",
            font=("Segoe UI", 9),
            foreground="#6e7d8d"
        )
        status_label.pack(anchor=tk.W)

        btn_frame = ttk.Frame(self.header_frame)
        btn_frame.pack(side=tk.RIGHT, padx=10)

        call_btn = ttk.Button(btn_frame, text="📞", width=3)
        call_btn.pack(side=tk.LEFT, padx=2)

        menu_btn = ttk.Button(btn_frame, text="⋮", width=3)
        menu_btn.pack(side=tk.LEFT, padx=2)

        # История сообщений
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

        self.chat_history = scrolledtext.ScrolledText(
            chat_frame,
            bg="#0e1621",
            fg="white",
            font=("Segoe UI", 11),
            wrap=tk.WORD,
            padx=15,
            pady=15,
            state=tk.DISABLED,
            insertbackground="white"
        )
        self.chat_history.pack(fill=tk.BOTH, expand=True)

        # Настройка тегов для форматирования сообщений
        self.chat_history.tag_configure("contact",
                                        background="#2A3B4C",
                                        lmargin1=20,
                                        lmargin2=20,
                                        rmargin=60,
                                        relief=tk.FLAT,
                                        spacing2=5,
                                        borderwidth=10,
                                        wrap=tk.WORD)

        self.chat_history.tag_configure("self",
                                        background="#2b5278",
                                        lmargin1=60,
                                        lmargin2=20,
                                        rmargin=20,
                                        relief=tk.FLAT,
                                        spacing2=5,
                                        justify=tk.RIGHT,
                                        borderwidth=10,
                                        wrap=tk.WORD)

    def create_message_input(self):
        # Панель ввода сообщений (располагается внизу)
        input_frame = ttk.Frame(self.root)
        input_frame.pack(fill=tk.X, padx=(0, 5), pady=(0, 5), side=tk.BOTTOM)

        # Верхняя линия разделителя
        separator = ttk.Frame(input_frame, height=1, style="Separator.TFrame")
        separator.pack(fill=tk.X, pady=(0, 5))

        # Контейнер для элементов ввода
        input_container = ttk.Frame(input_frame)
        input_container.pack(fill=tk.X, padx=5, pady=5)

        # Кнопки вложений
        attach_frame = ttk.Frame(input_container, width=40)
        attach_frame.pack(side=tk.LEFT, fill=tk.Y)

        attach_btn = ttk.Button(attach_frame, text="📎", width=3)
        attach_btn.pack(side=tk.TOP, padx=2)

        emoji_btn = ttk.Button(attach_frame, text="😊", width=3)
        emoji_btn.pack(side=tk.TOP, padx=2, pady=5)

        # Поле ввода сообщения
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(
            input_container,
            textvariable=self.message_var,
            font=("Segoe UI", 11)
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.focus_set()

        # Кнопка отправки
        send_btn = ttk.Button(
            input_container,
            text="Отправить",
            command=self.send_message,
            width=10
        )
        send_btn.pack(side=tk.RIGHT)

    def load_contacts(self):
        self.contact_list.delete(0, tk.END)
        for contact in sorted(self.contacts.keys()):
            self.contact_list.insert(tk.END, contact)

        # Выделить текущий чат
        try:
            idx = list(self.contacts.keys()).index(self.current_chat)
            self.contact_list.selection_set(idx)
            self.contact_list.see(idx)
        except ValueError:
            pass

    def load_chat_history(self):
        self.chat_history.config(state=tk.NORMAL)
        self.chat_history.delete(1.0, tk.END)

        for sender, text in self.contacts[self.current_chat]:
            tag = "contact" if sender != "Я" else "self"
            self.chat_history.insert(tk.END, text + "\n", tag)
            self.chat_history.insert(tk.END, "\n")

        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.yview(tk.END)

    def add_message(self, text, sender="Я"):
        # Добавить сообщение в историю
        self.chat_history.config(state=tk.NORMAL)
        tag = "self" if sender == "Я" else "contact"
        self.chat_history.insert(tk.END, text + "\n", tag)
        self.chat_history.insert(tk.END, "\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.yview(tk.END)

        # Сохранить в данных
        self.contacts[self.current_chat].append((sender, text))

    def send_message(self, event=None):
        message = self.message_var.get().strip()
        if message:
            self.add_message(message)
            self.message_var.set("")

            # Автоответ для Максима
            if self.current_chat == "Максим":
                replies = [
                    "Yeah-yeah, я тоже передаю вам привет, абсолютно мне незнакомый прохожий под именем Алекс. Меня зовут Максим и мне 48 лет.",
                    "Моё хобби есть быть есть гамбургер, я люблю иметь дом, иметь жену, иметь собаку и иметь детей.",
                    "Я имею своих детей как один брат и одна сестра. У сестры тоже есть работу во рту.",
                    "Оу, no, не важно. А давайте вы покажите, как вы любите иметь собака на улице?"
                ]
                if len(self.contacts[self.current_chat]) == 9:
                    time.sleep(10)
                    exit(0)
                # Выбираем ответ в зависимости от длины истории
                idx = (len(self.contacts[self.current_chat]) - 1) // 2
                self.root.after(2000, lambda: self.add_message(replies[idx], "Максим"))

    def switch_chat(self, event=None):
        # Переключение на выбранный чат
        selected = self.contact_list.curselection()
        if selected:
            self.current_chat = self.contact_list.get(selected[0])
            self.chat_title.config(text=self.current_chat)
            self.load_chat_history()
            self.update_avatar()

    def update_avatar(self):
        # Обновление аватарки в заголовке чата
        if self.current_chat == "Максим" and self.avatar_photo:
            self.avatar_label.configure(image=self.avatar_photo)
        else:
            # Для других контактов - инициалы
            self.avatar_label.configure(image='')
            self.avatar_label.configure(
                text=self.current_chat[0],
                font=("Segoe UI", 14, "bold"),
                background="#3d5466",
                foreground="white",
                width=3,
                anchor=tk.CENTER,
                relief=tk.FLAT
            )

    def create_new_chat(self):
        # Создание нового чата
        contact = simpledialog.askstring("Новый чат", "Введите имя контакта:", parent=self.root)
        if contact and contact.strip():
            contact = contact.strip()
            if contact in self.contacts:
                messagebox.showinfo("Ошибка", f"Чат с {contact} уже существует")
                return

            self.contacts[contact] = []
            self.load_contacts()

            # Выбрать новый чат
            idx = list(self.contacts.keys()).index(contact)
            self.contact_list.selection_clear(0, tk.END)
            self.contact_list.selection_set(idx)
            self.contact_list.see(idx)
            self.current_chat = contact
            self.chat_title.config(text=self.current_chat)
            self.update_avatar()
            self.load_chat_history()

    def filter_contacts(self, event):
        # Фильтрация контактов по поиску
        search_term = self.search_var.get().lower()
        self.contact_list.delete(0, tk.END)

        for contact in self.contacts:
            if search_term in contact.lower():
                self.contact_list.insert(tk.END, contact)

        # Попытаться сохранить выделение текущего чата
        if self.current_chat in self.contacts and search_term in self.current_chat.lower():
            idx = list(self.contacts.keys()).index(self.current_chat)
            self.contact_list.selection_set(idx)
            self.contact_list.see(idx)


if __name__ == "__main__":
    root = tk.Tk()
    app = XAMMessenger(root)
    app.update_avatar()  # Инициализация аватарки
    root.mainloop()
