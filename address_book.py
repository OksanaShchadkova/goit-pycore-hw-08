import pickle
from collections import UserDict
import re
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
        if not self.validate(value):
            raise ValueError("Phone number must be a string of 10 digits.")
        super().__init__(value)

    @staticmethod
    def validate(value):
        return re.match(r'^\d{10}$', value) is not None


class Birthday(Field):
    def __init__(self, value):
        if not self.validate(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)

    @staticmethod
    def validate(value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
            return True
        except ValueError:
            return False


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        if phone:
            self.phones.remove(phone)
        else:
            raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone, new_phone):
        if not Phone.validate(new_phone):
            raise ValueError("New phone number must be a string of 10 digits.")
        phone = self.find_phone(old_phone)
        if phone:
            self.remove_phone(old_phone)
            self.add_phone(new_phone)
        else:
            raise ValueError("Old phone number not found.")

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def __str__(self):
        phones = ", ".join(str(p) for p in self.phones) or "No phones"
        birthday = str(self.birthday) if self.birthday else "No birthday"
        return f"Name: {self.name}, Phones: {phones}, Birthday: {birthday}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = datetime.now().date()
        for record in self.data.values():
            if record.birthday:
                bday = datetime.strptime(
                    record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday.replace(year=today.year)
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(
                        year=today.year + 1)
                delta = (bday_this_year - today).days
                if 0 <= delta < 7:
                    greeting_day = bday_this_year
                    if greeting_day.weekday() in (5, 6):  # вихідні
                        greeting_day += timedelta(days=(7 -
                                                  greeting_day.weekday()))
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "congratulate_on": greeting_day.strftime("%d.%m.%Y")
                    })
        return upcoming_birthdays


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Not enough arguments."
    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.get(name)
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
    record = book.get(name)
    if record is None:
        raise ValueError("Contact not found.")
    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.get(name)
    if record:
        return f"Phones for {name}: {', '.join(str(phone) for phone in record.phones)}"
    else:
        raise KeyError


@input_error
def all_contacts(args, book):
    return "\n".join([str(record) for record in book.values()])


@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.get(name)
    if record is None:
        raise ValueError("Contact not found.")
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.get(name)
    if record:
        return f"{name}'s birthday: {record.birthday if record.birthday else 'No birthday added.'}"
    else:
        raise KeyError


@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    return "\n".join([f"{entry['name']} - {entry['congratulate_on']}" for entry in upcoming_birthdays]) if upcoming_birthdays else "No upcoming birthdays."


def main():
    book = load_data()  # Завантажуємо з файлу
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        if user_input.strip() == "":
            continue
        parts = user_input.strip().split()
        command, *args = [p.lower() if i == 0 else p for i,
                          p in enumerate(parts)]

        if command in ["close", "exit"]:
            save_data(book)  # Зберігаємо у файл
            print("Good bye! Contacts saved.")
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
            print(all_contacts(args, book))

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
