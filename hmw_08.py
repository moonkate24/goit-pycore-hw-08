import re
import pickle
from collections import UserDict
from datetime import datetime, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if self.validate(value):
            super().__init__(value)
        else:
            raise ValueError(f"Invalid phone number: {value}")

    @staticmethod
    def validate(value):
        pattern = re.compile(r'^\d{10}$')
        return bool(pattern.match(value))

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, '%d.%m.%Y').date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
                break

    def find_phone(self, phone):
        return any(p.value == phone for p in self.phones)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        if self.birthday:
            return self.birthday.value.strftime('%d.%m.%Y')
        return "No birthday set."

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            next_birthday = self.birthday.value.replace(year=today.year)
            if next_birthday < today:
                next_birthday = next_birthday.replace(year=today.year + 1)
            return (next_birthday - today).days
        return None

    def __str__(self):
        phones = ', '.join(str(phone) for phone in self.phones)
        birthday = self.show_birthday() if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.now().date()
        upcoming_birthdays = []
        for record in self.data.values():
            if record.birthday:
                next_birthday = record.birthday.value.replace(year=today.year)
                if next_birthday < today:
                    next_birthday = next_birthday.replace(year=today.year + 1)
                if 0 <= (next_birthday - today).days <= days:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

    def __str__(self):
        return '\n'.join(str(record) for record in self.data.values())

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please"
        except KeyError:
            return "Enter user name"
        except IndexError:
            return "Enter the argument for the command"
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        return "Contact not found."

@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return ', '.join(phone.value for phone in record.phones)
    else:
        return "Contact not found."

@input_error
def show_all(args, book):
    if book.data:
        return '\n'.join(str(record) for record in book.data.values())
    else:
        return "No contacts saved."

@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        return "Contact not found."

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record:
        return record.show_birthday()
    else:
        return "Contact not found."

@input_error
def birthdays(args, book):
    upcoming = book.get_upcoming_birthdays()
    if upcoming:
        return '\n'.join(str(record) for record in upcoming)
    else:
        return "No upcoming birthdays."

def parse_input(user_input):
    return user_input.strip().split()

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
