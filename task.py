from __future__ import annotations

from decimal import *
import re
from datetime import date, timedelta
from dataclasses import dataclass


@dataclass
class Credit:
    borrower: Client
    lender: Bank
    amount: int
    interest: Decimal
    deadline: date
    start_date: date
    deadline_pushed: int


class Client:

    def __init__(self, name, surname, age):
        self.name = name
        self.surname = surname
        self.age = age
        self.account_number = ''

    def change_bank(self, from_bank, to_bank):
        amount = from_bank.remove_client(self)

        if amount is not None:
            to_bank.add_client(self, initial_deposit=amount)
            return '{} changed from bank {} to {}'.format(self.full_name, from_bank.name, to_bank.name)

        return '{} failed to change banks'.format(self.full_name)

    @classmethod
    def from_bank(cls, bank, name, surname, age):
        client = cls(name, surname, age)
        bank.add_client(client)
        return client

    @property
    def full_name(self):
        return self.name + ' ' + self.surname

    @full_name.setter
    def full_name(self, value):
        names = value.split()

        if len(names) != 2:
            return

        self.name = names[0]
        self.surname = names[1]


class Bank:

    def __init__(self, name, credit_interest):
        self.clients = {}
        self.client_infos = []
        self.name = name
        self.credit_interest = credit_interest
        self.credits = []
        getcontext().prec = 4

    def get_shortname(self):
        return re.sub('[^A-Z]', '', self.name)

    @staticmethod
    def delay_credit(credit):
        month = credit.deadline.month + 1
        year = credit.deadline.year
        day = credit.deadline.day

        if month > 12:
            month = 1
            year += 1

        credit.deadline = date(year, month, day)
        credit.interest += Decimal(0.01)

    def add_client(self, client, initial_deposit=None):
        client.account_number = self.get_shortname() + str(len(self.clients))
        self.clients[client.account_number] = initial_deposit if initial_deposit is not None else 0
        self.client_infos.append(client)

    def remove_client(self, client):
        if client.account_number in self.clients:
            amount = self.clients.pop(client.account_number)
            self.client_infos.remove(client)
            return amount

        return None

    def get_client_names(self):
        names = ''

        for client in self.client_infos:
            names += client.full_name + ', ' + str(client.age) + '\n'

        return names

    def get_account_balance_for(self, client):
        if client.account_number in self.clients:
            return '{} {}\'s account balance : {}'.format(client.name, client.surname,
                                                          self.clients[client.account_number])

        return 'Cannot find account attached to {} {}'.format(client.name, client.surname)

    def money_deposit(self, client, amount):
        if client.account_number in self.clients:
            self.clients[client.account_number] += amount
            return 'Success'

        return 'Cannot find account attached to {} {}'.format(client.name, client.surname)

    def money_withdrawal(self, client, amount):
        acc_number = client.account_number

        if acc_number in self.clients:
            if self.clients[acc_number] >= amount:
                self.clients[acc_number] -= amount
                return 'Success'
            else:
                return 'Account balance too low'

        return 'Cannot find account attached to {} {}'.format(client.name, client.surname)

    def money_transfer(self, from_client, amount, to_client, dest_bank=None):
        withdrawal_status = self.money_withdrawal(from_client, amount)

        if dest_bank is None:
            dest_bank = self

        if withdrawal_status == 'Success':
            deposit_status = dest_bank.money_deposit(to_client, amount)

            if deposit_status == 'Success':
                return 'Success'
            else:
                self.money_deposit(from_client, amount)
                return deposit_status

        return withdrawal_status

    def lend_money_to(self, client, amount, start_date, deadline):
        if client.account_number in self.clients:
            self.credits.append(Credit(borrower=client, lender=self, amount=amount,
                                       interest=Decimal(self.credit_interest), deadline=deadline,
                                       start_date=start_date, deadline_pushed=0))
            self.clients[client.account_number] += amount

    def credit_reimbursement(self, todays_date):
        i = 0
        summary = ''
        today = todays_date  # would normally be date.today()

        for credit in self.credits:

            if credit.deadline <= today:
                summary += '{}\'s credit has ended today\n'.format(credit.borrower.full_name)
                self.credits.pop(i)
                continue

            if (today.day == 1 and today > credit.start_date) or today == credit.start_date:
                num_months = (credit.deadline.year - credit.start_date.year) * 12 + (
                        credit.deadline.month - credit.start_date.month) + 1 - credit.deadline_pushed
                amount_to_pay = Decimal(credit.amount / num_months) * (Decimal(1) + credit.interest)

                if self.clients[credit.borrower.account_number] >= amount_to_pay:
                    self.clients[credit.borrower.account_number] -= amount_to_pay
                    summary += '{} reimbursed {} of his credit to the bank\n'.format(credit.borrower.full_name,
                                                                                     amount_to_pay)
                else:
                    Bank.delay_credit(credit)
                    credit.deadline_pushed += 1
                    summary += 'Not enough money on {}\'s account to reimburse the credit: deadline has been pushed ' \
                               'by a month\n'.format(credit.borrower.full_name)
                    summary += 'Credit interests have been increased to {}'.format(credit.interest)

            i += 1

        return summary


if __name__ == "__main__":
    bnp = Bank('BNP Paribas', credit_interest=0.06)
    sg = Bank('Societe Generale', credit_interest=0.05)
    credit_agricole = Bank('Credit Agricole', credit_interest=0.035)

    boris = Client.from_bank(bnp, 'Ivanovic', 'Boris', 23)
    john = Client.from_bank(bnp, 'Doe', 'John', 26)
    jane = Client.from_bank(bnp, 'Doe', 'Jane', 21)
    tom = Client.from_bank(sg, 'Cobley', 'Tom', 45)
    joe = Client.from_bank(sg, 'Bloggs', 'Joe', 32)
    fred = Client.from_bank(sg, 'Nerk', 'Fred', 27)
    juan = Client.from_bank(credit_agricole, 'Perez', 'Juan', 24)
    alan = Client.from_bank(credit_agricole, 'Fresco', 'Alan', 41)
    dylan = Client.from_bank(credit_agricole, 'Meringue', 'Dylan', 37)
    hans = Client.from_bank(credit_agricole, 'Down', 'Hans', 33)
    abraham = Client.from_bank(credit_agricole, 'Pigeon', 'Abraham', 29)
    max_c = Client.from_bank(credit_agricole, 'Conversion', 'Max', 56)

    print('+------ BNP Paribas clients -----+')
    print(bnp.get_client_names())

    print('+------ Societe Generale clients -----+')
    print(sg.get_client_names())

    print('+------ Credit Agricole clients -----+')
    print(credit_agricole.get_client_names())

    print('+------ Money deposit -----+')

    print('2000€ deposit on Boris account : {}'.format(bnp.money_deposit(boris, 2000)))
    print('1500€ deposit on John\'s account : {}'.format(bnp.money_deposit(john, 1500)))
    print('1000€ deposit on Joe\'s account : {}'.format(sg.money_deposit(joe, 1000)))
    print('1000€ deposit on Dylan\'s account : {}\n'.format(credit_agricole.money_deposit(dylan, 1000)))

    print('+------ Money withdrawal -----+')

    print('500€ cash withdrawal from Boris : {}'.format(bnp.money_withdrawal(boris, 500)))
    print('100€ cash withdrawal from John : {}'.format(bnp.money_withdrawal(john, 100)))
    print('200€ cash withdrawal from Joe : {}'.format(sg.money_withdrawal(joe, 200)))
    print('300€ cash withdrawal from Dylan : {}\n'.format(credit_agricole.money_withdrawal(dylan, 300)))

    print('+----- Money transfer -----+')

    print('100€ transfer from Boris to John (same bank) : {}'.format(bnp.money_transfer(boris, 100, john)))
    print('100€ transfer from John to Dylan (different bank) : {}'.format(bnp.money_transfer(john, 100, dylan,
                                                                                             dest_bank=credit_agricole)))
    print('500€ transfer from Joe to Boris (different bank) : {}'.format(sg.money_transfer(joe, 500, boris,
                                                                                           dest_bank=bnp)))
    print('500€ transfer from Dylan to Boris (different bank) : {}\n'.format(credit_agricole.money_transfer(dylan, 500, boris,
                                                                                                dest_bank=bnp)))

    print('+----- Bank change -----+')

    print('{}\n'.format(boris.change_bank(bnp, sg)))

    print('+------ BNP Paribas clients -----+')
    print(bnp.get_client_names())

    print('+------ Societe Generale clients -----+')
    print(sg.get_client_names())

    print('+----- Account balances -----+')

    print(sg.get_account_balance_for(boris))
    print(bnp.get_account_balance_for(john))
    print(sg.get_account_balance_for(joe))
    print(credit_agricole.get_account_balance_for(dylan))

    print('\n+----- Credit Simulation for Boris -----+')

    today = date.today()

    start_date = date(today.year + 1 if today.month == 12 else today.year,
                      today.month + 1 if today.month <= 11 else 1,
                      today.day)

    deadline = date(today.year + 1 if today.month >= 8 else today.year,
                    today.month + 5 if today.month <= 7 else (today.month + 5) % 12,
                    today.day)

    print('Simulating the reimbursement of a credit starting on {} and ending on {}'.format(start_date, deadline))
    print('5000€ are lended to Boris with a 5% interest rate')

    sg.lend_money_to(boris, 5000, start_date, deadline)
    print('{}\n'.format(sg.get_account_balance_for(boris)))

    current_date = start_date

    summary = ''

    while (summary is None or (summary is not None and summary.find('has ended') == -1)) and current_date.year <= 2022:
        summary = sg.credit_reimbursement(current_date)

        if summary:
            print('+--- {} ---+\n'.format(current_date))
            print(summary)

        current_date = current_date + timedelta(1)

    print(sg.get_account_balance_for(boris))
