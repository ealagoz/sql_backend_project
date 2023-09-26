# Simple banking system
import random
import sqlite3
import sys


# SQLITE3 functions
# create a database connection
try:
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS card (
                id INTEGER PRIMARY KEY,
                number TEXT NOT NULL UNIQUE,
                pin TEXT NOT NULL,
                balance INTEGER DEFAULT 0
                );
                """)
    conn.commit()
except sqlite3.Error as e:
    print(e)


class BankAccount:

    def __init__(self, card_number=None, card_pin=None, balance=None) -> None:
        self.card_number = card_number
        self.card_pin = card_pin
        self.INN = 400000  # issuer identification no
        self.checkSum = 8  # card's last digit
        self.balance = balance

    def create_account(self) -> str:
        self.card_number = str(self.INN) + \
            str(random.randint(100000000, 999999999)) + \
            str(self.checkSum)
        return self.card_number

    def is_card_number_valid(self, card_number: str) -> int:
        """
        Check generated card number validity using Luhn Algorithm
        1. Drop last digit
        2. Multiply odd index digits by 2
        3. Subtract 9 from digits greater than 9
        4. Sum digits. Sum has to be multiple of 10
        For example Sum = 57, needs 3 to 60 to satisfy 10x rule
        5. Add number needed for 10X rule as the last digit of
        the original generated card number.

        Return an int card number
        """
        # drop last digit and copy to a tmp list
        tmp_card_number = list(map(int, card_number[:-1]))
        new_card_number = []

        # loop over digits
        for index, num in enumerate(tmp_card_number, start=1):
            # multiply odd index digits by 2
            if index % 2 == 1:
                # subtract 9 from digits greater than 9
                if num * 2 > 9:
                    new_card_number.append((num * 2) - 9)
                else:
                    new_card_number.append(num * 2)
            else:
                new_card_number.append(num)

        # sum all digits
        total, last_digit = 0, 0
        for num in new_card_number:
            total += int(num)

        # Find sums nearest multiple of 10
        # and append determined last digit to card number
        last_digit = 10 - (total % 10)
        if last_digit < 10:
            tmp_card_number.append(last_digit)
        else:
            tmp_card_number.append(0)

        self.card_number = int("".join(map(str, tmp_card_number)))
        # print("Receiver card last digit: ", last_digit)

        if last_digit != int(card_number[-1]):
            return 1
        else:
            return 2

    def create_card_pin(self):
        self.card_pin = random.randint(1000, 9999)
        return self.card_pin

    def user_login(self, user_input_card, user_pin_card) -> int:
        # get card number and pin from database
        log_query = read_card(user_input_card, user_pin_card)
        if log_query is None:
            return 1
        else:
            self.card_number = log_query[1]
            self.card_pin = log_query[2]
            self.balance = log_query[3]
            return 2

    def account_balance(self, user_card, user_pin) -> int:
        balance_query = read_card(user_card, user_pin)
        # print("Query results for balance: ", balance_query)
        if balance_query is not None:
            self.balance = balance_query[3]
            return self.balance
        else:
            print("Error: Unable to retrieve balance!")

    def add_income(self, user_card, income):
        self.balance += income
        update_balance(self.balance, user_card)
        return self.balance

    def remove_income(self, user_card, amount):
        print("Balance before: ", self.balance)
        print("Card number: ", self.card_number, "Car pin: ", self.card_pin)
        self.balance -= int(amount)
        print("Balance after1: ", self.balance)
        update_balance(self.balance, user_card)
        print("Balance after2: ", self.balance)
        return self.balance

    def do_transfer(self, card_number):
        result = transfer_card(card_number)
        if result is None:
            return 1
        else:
            self.card_number = result[1]
            return 2

    def remove_card(self, card_number):
        delete_card(card_number)


# generate class instance
bank_account = BankAccount()


def add_card(card_number, card_pin):
    with conn:
        cur.execute("INSERT INTO card (number, pin) VALUES (:number, :pin);",
                    {"number": card_number, "pin": card_pin})
    # finally:
    #     conn.close()


def read_card(card_number, card_pin):
    cur.execute("SELECT * FROM card WHERE number = :number AND pin = :pin;",
                {"number": card_number, "pin": card_pin})
    return cur.fetchone()


def transfer_card(card_number):
    cur.execute("SELECT * FROM card WHERE number = :number;",
                {"number": card_number})
    return cur.fetchone()


def update_balance(balance, card_number):
    with conn:
        cur.execute("UPDATE card SET balance = :balance WHERE number = :card_number;",
                    {"balance": balance, "card_number": card_number})


def delete_card(card_number):
    with conn:
        cur.execute("DELETE FROM card WHERE number = :card_number;",
                    {"card_number": card_number})


# options for users to select
options_login = ["Create an account", "Log into account", "Exit"]
options_account = ["Balance", "Add income",
                   "Do transfer", "Close account", "Log out", "Exit"]


# print login options
def login_options():
    for i, option in enumerate(options_login):
        if option == "Exit":
            print(f"0. {option}")
        else:
            print(f"{i + 1}. {option}")


# options for account
def account_options():
    for i, option in enumerate(options_account):
        if option == "Exit":
            print(f"0. {option}")
        else:
            print(f"{i + 1}. {option}")


# check entered choice and perform corresponding action
while True:
    # get the users input
    login_options()
    choice = int(input())
    if choice == 0:
        print("Bye !")
        conn.close()
        sys.exit()

    elif choice == 1:
        bank_account.create_account()
        bank_account.is_card_number_valid(bank_account.card_number)
        bank_account.create_card_pin()

        print("Your card has been created")
        print("Your card number: ")
        print(bank_account.card_number)
        print("Your card PIN: ")
        print(bank_account.card_pin)

        # add card to database
        add_card(bank_account.card_number, bank_account.card_pin)

        # print updated card table
        # bank_account.database_info()

    elif choice == 2:
        # ask for user input
        user_card_input = int(input("Enter your card number: "))
        user_card_pin = int(input("Enter your PIN: "))
        # check user input in database
        # bank_account.user_login(user_card_input, user_card_pin)
        account_output = bank_account.user_login(
            user_card_input, user_card_pin)

        if account_output == 2:
            print("\nYou have successfully logged in!\n")
            while True:
                account_options()
                account_choice = int(input())
                if account_choice == 0:
                    print("Bye !")
                    conn.close()
                    sys.exit()  # Exit the account menu
                elif account_choice == 1:
                    print("\nBalance: ", bank_account.account_balance(user_card_input,
                                                                      user_card_pin), " \n")
                elif account_choice == 2:
                    new_income = int(input("Enter income: "))
                    bank_account.add_income(user_card_input, new_income)
                    print("\nIncome was added!\n")
                elif account_choice == 3:
                    print("Transfer")
                    receiver_card = input("Enter card number: ")
                    # check if receiver card is valid
                    if bank_account.is_card_number_valid(receiver_card) == 1:
                        print(
                            "\nProbably you made a mistake in the card number. Please try again!\n")
                        continue
                    else:
                        # check if receiver card exists in database
                        if transfer_card(receiver_card) is None:
                            print("\nSuch a card does not exist.\n")
                            continue
                        else:
                            transfer_amount = input(
                                "Enter how much money you want to transfer: ")
                            if int(transfer_amount) > bank_account.balance:
                                print("\nNot enough money!\n")
                                continue
                            else:
                                bank_account.remove_income(
                                    user_card_input, transfer_amount)
                                update_balance(transfer_amount, receiver_card)
                                print("\nSuccess!\n")
                elif account_choice == 4:
                    bank_account.remove_card(user_card_input)
                    print("\nThe account has been closed!\n")
                    break
                elif account_choice == 5:
                    print("\nYou have successfully logged out!\n")
                    break
        elif account_output == 1:
            print("\nWrong card number of PIN!\n")
            continue  # back to options_login menu
    else:
        print("Invalid choice")
