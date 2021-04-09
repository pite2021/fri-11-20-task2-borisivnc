import random


class Client:

  def __init__(self, name, surname, age):
    self.name = name
    self.surname = surname
    self.age = age
    self.money = 0
    self.account_number = random.randrange(10000, 99999)



class Bank:

  def __init__(self, name):
    self.clients = []
    self.name = name

  def add_client(self, client):
    self.clients.append(client)

  def display_account_balance(self, account_number):
    for i in range(len(self.clients)):
      if self.clients[i].account_number == account_number: 
        print('{} {}\'s account balance : {}'.format(self.clients[i].name, self.clients[i].surname, self.clients[i].money))
        return
    
    print('No account with this number found')

  def money_input(self, account_number, amount):

    for i in range(len(self.clients)):
      if self.clients[i].account_number == account_number: 
        client = self.clients[i]
        client.money += amount
        print('Money successfully withdrawed')
        return True
      
    return False

  def money_withdrawal(self, account_number, amount):

    for i in range(len(self.clients)):
      if self.clients[i].account_number == account_number: 
        client = self.clients[i]

        if client.money < amount:
          print('{} {}\'s account balance is too low to withdraw money.'.format(client.name, client.surname))
          return 1

        else:
          client.money -= amount
          print('Money successfully withdrawed')
          return 0
        
        return 2

  def money_transfer(self, src, to, amount):

    money_w = self.money_withdrawal(src, amount)
    
    if money_w == 0:
      if self.money_input(to, amount):
        print('Money transfer successfull')
      else:
        print('{} account number was not found in the bank'.format(to))
    elif money_w == 2 :
      print('{} account number was not found in the bank'.format(src))

  


bnp = Bank('BNP Paribas')

boris = Client('Ivanovic', 'Boris', 23)
john = Client('Doe', 'John', 23)

# For the sake of the example 
boris.money = 100
john.money = 100

bnp.add_client(boris)
bnp.add_client(john)

bnp.money_transfer(boris.account_number, john.account_number, 50)
bnp.display_account_balance(boris.account_number)
bnp.display_account_balance(john.account_number)