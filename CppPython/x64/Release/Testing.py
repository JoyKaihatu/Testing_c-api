import numpy as np
import random


class Utility:
  def print_board(self,board):
    for row in board:
      print("  ".join([str(c.name[0] if c is not None else ".") for c in row]))

  def get_object(self, obj):
    class A(obj):
      print("Berhasil")
    return A
  


class MCTSNode:
    def __init__(self, parent, board_state, character_to_play, character_list, character_index, move=None) -> None:
        self.parent = parent
        self.board = board_state
        self.character_play = character_to_play
        self.character_index = character_index
        self.character_list = character_list
        self.move = move
        self.visits = 0
        self.wins = 0
        self.children = {}

    def is_terminal(self):
        if all(char.team =="Dead" for char in self.character_list if char.team != "ally"):
            return True
        elif all(char.team == "Dead" for char in self.character_list if char.team != 'Enemy'):
            return True
        else:
            return False
        
    def is_fully_expanded(self, board_state):
        a = self.get_possible_moves(board_state)
        for move in a:
            if move not in self.children:
                return False
        return True

    def get_possible_moves(self, board_state):
        a = []# Default Action = Move
        if self.character_play.bisa_serang(board_state):
            a.append(1) # Kalau bisa atk (Ada musuh in range untuk di serang) Maka opsi atk, terbuka
            a.append(0)
        else:
            a.append(0)
        return a

class MCTSAI:
    def __init__(self) -> None:
        self.C = 1.41 # Parameter Bebas
        

    def find_best_move(self, simulations, who_play, characters_list, board):
        self.characters = characters_list
        self.board = board
        self.root = MCTSNode(None, self.board, self.characters[who_play],self.characters,who_play)

        if self.characters[who_play].bisa_serang(self.board) == False:
            return 0

        for _ in range(simulations):
            self.simulate(self.board)

        picked_child = self.get_most_visited_child(self.root)

        print("ALL BEST MOVE LISTED")
        for move, child in self.root.children.items():
          print("-----------------------")
          print("Move: ",move)
          print("Visits: ",child.visits)
          print("Wins: ",child.wins)

        picked_move = picked_child.move

        return picked_move

    def get_most_visited_child(self, node:MCTSNode):
        most_visited = None
        max_visits = float('-inf')

        for move, child in node.children.items():
            if child.visits > max_visits:
                max_visits = child.visits
                most_visited = child
        return most_visited

            

    def simulate(self, board):
        current_node = self.root
        while not current_node.is_terminal():
              # if current_node is None:
              #   break
              current_node = self.select_node(current_node, board)
              # if current_node is None:
              #   break

              current_node = self.expand_node(current_node, board)
              # if current_node is None:
              #   break
              winner = self.rollout(current_node, board)

              current_node = self.backpropagate(current_node, winner)

              if current_node is None:
                 break




    def backpropagate(self, node:MCTSNode, winner):
        while node is not None:
          node.visits += 1
          if winner == 'Enemy':
              node.wins += 1

          node = node.parent
        return node



    def rollout(self, node:MCTSNode, board):
        winner = self.do_random_games(node, board.copy())

        return winner

    def do_random_games(self, node:MCTSNode, board):
        ally_hp = 0
        enemy_hp = 0
        play = node
        character_list = play.character_list
        index = play.character_index
        for _ in range(10):
            if index > len(character_list) - 1:
                index = 0
            if character_list[index].team != 'Dead':
                character_list[index].take_turn_random(board)
            
            index += 1

        for char in character_list:
            if char.team == 'Ally':
                ally_hp += char.health
            elif char.team == 'Enemy':
                enemy_hp += char.health
        
        if enemy_hp > ally_hp:
            return 'Enemy'
        elif ally_hp >= enemy_hp:
            return 'Ally'

    def select_node(self, node:MCTSNode, board):
        while node is not None and not node.is_terminal():
            if not node.is_fully_expanded(board):
                return self.expand_node(node, board)
            node = self.select_child_ucb(node)
        return node

    def expand_node(self, node:MCTSNode, board):
        a = node.get_possible_moves(board)
        
        for move in a:
            if move not in node.children:
                print("Board di dalam expand_node: ", move)
                a = Utility()
                a.print_board(board)
                print("")
                new_board_state, chara_list_inCurrState = self.perform_move(board.copy(), node, move)
                next_character = self.get_next_character(node)
                child = MCTSNode(node,new_board_state,chara_list_inCurrState[next_character],chara_list_inCurrState, next_character, move)
                node.children[move] = child
        return node
    
    def select_child_ucb(self, node:MCTSNode):
        best_ucb = float('-inf')
        best_child = None
        
        for move, child in node.children.items():
            if child.visits == 0:
                return child
            ucb = child.wins / child.visits + self.C * np.sqrt(np.log(node.visits) / child.visits)

            if ucb > best_ucb:
                best_ucb = ucb
                best_child = child

        return best_child
                

    def get_next_character(self,node:MCTSNode):
        current_turn = node.character_index
        print(node.character_list)
        character_list = node.character_list
        next_turn = current_turn

        a = all(i.team == 'Dead' for i in character_list)

        while not a:
            print(a)
            current_turn += 1
            if current_turn > len(character_list) - 1:
                current_turn = 0
            print(character_list[current_turn].name, "Health: ", character_list[current_turn].health)
            if character_list[current_turn].health > 0:
                next_turn = current_turn
                break
            a = all(i.team == 'Dead' for i in character_list)
            if a:
               break
        return next_turn

    

    def perform_move(self, board, node:MCTSNode, move):
        print("board di dalam perform move")
        a = Utility()
        a.print_board(board)

        chara_list = node.character_list.copy()
        chara_index = node.character_index
        current_char = chara_list[chara_index]


        current_x = 0
        current_y = 0
        character = current_char
        print(" ")
        if move == 0: # Action = MOVE
            x_target, y_target = character.move_on_target(board)
            character.move(board, x_target, y_target)
        elif move == 1:
            x_target, y_target = character.attack_on_target(board)
            character.attack(board, x_target, y_target)
            

        return board, chara_list



class Character:
  def __init__(self, name, team, x, y, index):
    self.index = index
    self.name = name
    self.team = team
    self.x = x
    self.y = y
    self.health = 100  # Adjust this for desired health

  def bisa_serang(self, board):
      x_min = self.x - 1
      if x_min < 0:
         x_min = 0
      x_max = self.x + 1
      if x_max > len(board) - 1:
         x_max = len(board) - 1
      y_min = self.y - 1
      if y_min < 0:
        y_min = 0
      y_max = self.y + 1
      if y_max > len(board) - 1:
         y_max = len(board) - 1
      for i in range(x_min, x_max):
        for j in range(y_min, y_max):
            if board[i][j] is not None and board[i][j].team != self.team:
              return True
      return False

  def can_move(self, board, x, y):
    # Check if new position is within board and not occupied
    if 0 <= x < len(board) and 0 <= y < len(board[0]) and board[x][y] is None:
      return True
    return False

  def can_attack(self, board, x, y):
    # Check if target is on adjacent tile and on enemy team
    if abs(self.x - x) <= 1 and abs(self.y - y) <= 1 and 0 <= x < len(board) and 0 <= y < len(board[0]):
      target = board[x][y]
      if target is not None and target.team != self.team:
        return True
    return False

  def move(self, board, x, y):
    if self.can_move(board, x, y):
        print("Di dalam sebelum move")
        print(self.x,self.y)
        a = Utility()
        a.print_board(board)
        print(" ")
        board[self.x][self.y] = None  # Clear old position
        self.x = x
        self.y = y
        board[x][y] = self  # Update new position

        print("Di dalam setelah move")
        print(self.x,self.y)
        a = Utility()
        a.print_board(board)
        print(" ")
        return False
    else:
      print("Selected Grid Out Of Range")
      return True

  def attack(self, board, x, y):
    if self.can_attack(board, x, y):
        target = board[x][y]
        target.health -= 10  # Adjust damage value
        print(f"{self.name} attacks {target.name} for 10 damage!")
        if target.health <= 0:
            board[x][y] = None  # Remove dead character
            self.team = 'Dead'
        return False
    else:
      print("Wrong Coordinate. No Enemy On Grid")
      return True

  def take_turn(self, board):
    a = True
    while a:
        print(f"{self.name} now on {self.x}, {self.y}")
        action = input(f"{self.name}'s turn ({self.health} HP). Move (M) or Attack (A)? ").upper()    
        if action == "M":
            # Get new position within movement range
            new_x = int(input("Enter X coordinate (within 2 spaces): "))
            new_y = int(input("Enter Y coordinate (within 2 spaces): "))
            a = self.move(board, new_x, new_y)
            if a is True:
              print("Move Invalid. Choose within 2 adjacent Range")

        elif action == "A":
            # Get target position within attack range
            new_x = int(input("Enter X coordinate of target: "))
            new_y = int(input("Enter Y coordinate of target: "))
            a = self.attack(board, new_x, new_y)
            
            if a is True:
              print("Coordinate Invalid or There are no Enemy in that grid")

  def take_turn_random(self, board):
      a = Utility()
      print("Board di dalam take_turn_random")
      a.print_board(board)
      print(' ')
      pick = None
      switchero = False
      if self.bisa_serang(board):
        pick = random.randint(0,1)
      else:
        pick = 0
      
      if pick == 1:
        x_target, y_target = self.attack_on_target(board)
        print(x_target, y_target, "Action: ATTACK")
        self.attack(board, x_target, y_target)

      elif pick == 0:
        x_target, y_target = self.move_on_target(board)
        print(x_target, y_target, "Action: MOVE")
        self.move(board, x_target, y_target)

  def ai_do_move(self, board, move):
    if move == 1:
        x_target, y_target = self.attack_on_target(board)
        print(x_target, y_target, "Action: ATTACK")
        self.attack(board, x_target, y_target)

    elif move == 0:
      x_target, y_target = self.move_on_target(board)
      print(x_target, y_target, "Action: MOVE")
      self.move(board, x_target, y_target)
      
  def attack_on_target(self, board):
    print("Board di dalam attack on target")
    a = Utility()
    a.print_board(board)
    print(" ")
    x_min = self.x - 1
    if x_min < 0:
      x_min = 0
    x_max = self.x + 1
    if x_max > len(board) - 1:
      x_max = len(board) - 1
    y_min = self.y - 1
    if y_min < 0:
      y_min = 0
    y_max = self.y + 1
    if y_max > len(board) - 1:
      y_max = len(board) - 1
    for i in range(x_min, x_max):
      for j in range(y_min, y_max):
          if board[i][j] is not None and board[i][j].team != self.team:
              return i, j
  def move_on_target(self, board):
      print("Board di dalam move_on_target")
      a = Utility()
      a.print_board(board)
      while True: 
          x_min = self.x - 2
          if x_min < 0:
            x_min = 0
          x_max = self.x + 2
          if x_max > len(board) - 1:
            x_max = len(board) - 1
          y_min = self.y - 2
          if y_min < 0:
            y_min = 0
          y_max = self.y + 2
          if y_max > len(board) - 1:
            y_max = len(board) - 1
          
          x_target = random.randint(x_min, x_max)
          y_target = random.randint(y_min, y_max)

          if x_target != self.x:
              if y_target == self.y:
                if board[x_target][y_target] is None:
                    break
              elif y_target != self.y:
                if board[x_target][y_target] is None:
                    break
          elif x_target == self.x:
              if y_target != self.y:
                if board[x_target][y_target] is None:
                    break
                
      return x_target, y_target

class Board:
  def __init__(self, width, height):
    self.width = width
    self.height = height
    self.board = [[None for _ in range(width)] for _ in range(height)]

  def place_character(self, character):
    self.board[character.x][character.y] = character

  def print_board(self):
    for row in self.board:
      print("  ".join([str(c.name[0] if c is not None else ".") for c in row]))


def main():
  
  # Create board, characters, and place them
  board = Board(8, 8)
  characters = [
      Character("Hero", "Ally", 1, 1, 0),
      Character("Goblin", "Enemy", 3, 3, 1),
      Character("Ogre", "Enemy", 4,4,2),
      Character("Priest", "Ally",0,0,3)
  ]
  for character in characters:
    board.place_character(character)

  return 1.0


