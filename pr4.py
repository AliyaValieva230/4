import threading
import json
import os
from cryptography.fernet import Fernet


def generate_key():
    return Fernet.generate_key()


class Note:
    def __init__(self, user):
        self.user = user
        self.notes = []
        self.lock = threading.Lock()
        self.key = self.load_key()
        self.cipher = Fernet(self.key)
        self.load_notes()

    def load_key(self):
        try:
            with open(f"{self.user}_key.key", "rb") as key_file:
                return key_file.read()
        except FileNotFoundError:
            new_key = generate_key()
            with open(f"{self.user}_key.key", "wb") as key_file:
                key_file.write(new_key)
            return new_key

    def load_notes(self):
        try:
            with open(f"{self.user}_notes.json", "r") as file:
                self.notes = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Заметок нет или файл повреждён, создаётся новая запись.")
            self.notes = []

    def save_notes(self):
        with self.lock:
            try:
                with open(f"{self.user}_notes.json", "w") as file:
                    json.dump(self.notes, file)
                print("Заметки успешно сохранены.")
            except Exception as e:
                print(f"Ошибка при сохранении заметок: {e}")

    def add_note(self, note):
        self.notes.append(note)
        self.save_notes()

    def encrypt_text(self, text):
        return self.cipher.encrypt(text.encode()).decode()

    def decrypt_text(self, encrypted_text):
        return self.cipher.decrypt(encrypted_text.encode()).decode()

    def encrypt_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                content = file.read()
            encrypted_content = self.encrypt_text(content)
            return encrypted_content
        except Exception as e:
            print(f"Ошибка при чтении файла: {e}")
            return None


class UserManager:
    def __init__(self):
        self.users_file = "users.json"
        self.load_users()

    def load_users(self):
        try:
            with open(self.users_file, "r") as file:
                self.users = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            print("Не удалось загрузить пользователей, создаётся новая запись.")
            self.users = {}

    def save_users(self):
        try:
            with open(self.users_file, "w") as file:
                json.dump(self.users, file)
            print("Пользователи успешно сохранены.")
        except Exception as e:
            print(f"Ошибка при сохранении пользователей: {e}")

    def register(self, username, password):
        if username in self.users:
            print("Пользователь уже существует!")
            return False
        self.users[username] = password
        self.save_users()
        print("Регистрация успешна!")
        return True

    def authenticate(self, username, password):
        if self.users.get(username) == password:
            print("Аутентификация успешна!")
            return True
        print("Неверное имя пользователя или пароль!")
        return False


def auto_save(note):
    while True:
        threading.Event().wait(5)
        note.save_notes()


def main():
    user_manager = UserManager()

    action = input("Выберите действие (регистрация/вход): ").strip().lower()
    username = input("Введите имя пользователя: ")
    password = input("Введите пароль: ")

    if action == "регистрация":
        user_manager.register(username, password)
    elif action == "вход":
        if not user_manager.authenticate(username, password):
            return
    else:
        print("Неизвестное действие!")
        return

    note = Note(username)

    save_thread = threading.Thread(target=auto_save, args=(note,), daemon=True)
    save_thread.start()
    while True:
        choice = input(
            "Выберите действие: \n1. Ввести текст\n2. Указать путь к файлу\n3. Расшифровать последнюю заметку\n4. Выход\nВаш выбор: ").strip()

        if choice == "1":
            note_text = input("Введите заметку: ")
            encrypted_note = note.encrypt_text(note_text)
            note.add_note(encrypted_note)
            print("Заметка добавлена и зашифрована.")
        elif choice == "2":
            file_path = input("Введите путь к файлу: ")
            encrypted_content = note.encrypt_file(file_path)
            if encrypted_content:
                note.add_note(encrypted_content)
                print("Содержимое файла зашифровано и добавлено в заметки.")
        elif choice == "3":
            if note.notes:
                last_encrypted_note = note.notes[-1]
                decrypted_note = note.decrypt_text(last_encrypted_note)
                print(f"Расшифрованная заметка: {decrypted_note}")
            else:
                print("Заметок для расшифровки нет.")
        elif choice == "4":
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
if __name__ == "__main__":
    main()
