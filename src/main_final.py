# coding: utf-8

import abc
from math import cos, sin, pi
from sys import stdin, setrecursionlimit
from re import match, sub, findall
from collections import deque

setrecursionlimit(500000)


 
UP, DOWN, LEFT, RIGHT, FORW, BACK, HEX, COLOR, PERIOD, REP, QUOTE, ERROR = 'UP', 'DOWN', 'LEFT', 'RIGHT','FORW', 'BACK', '#', 'COLOR', '.', 'REP', '"', "ERROR"


class Token:
    def __init__(self, token, row, value=None): 
        self.token = token
        self.row = row
        self.value = value


# Klass som går igenom input strängen och gör om dessa till tokens 
class LexAnalysator:
    
    def __init__(self, input):
        self.analyser = deque()
        self.input = input
        self.row = 1
    

    # Delar upp input strängen i tokens
    def add_tokens(self, input_list):
        for token in input_list:
            if token[0:4] == 'FORW'    : self.analyser.append(Token(FORW, self.row))
            elif token[0:4] == 'BACK'  : self.analyser.append(Token(BACK, self.row))
            elif token[0:4] == 'LEFT'  : self.analyser.append(Token(LEFT, self.row))        
            elif token[0:5] == 'RIGHT' : self.analyser.append(Token(RIGHT, self.row))        
            elif token      == "DOWN"  : self.analyser.append(Token(DOWN, self.row))
            elif token      == "UP"    : self.analyser.append(Token(UP, self.row))
            elif token[0:5] == 'COLOR' : self.analyser.append(Token(COLOR, self.row)) 
            elif token[0:3] == "REP"   : self.analyser.append(Token(REP, self.row, token)) 
            elif token      == '.'     : self.analyser.append(Token(PERIOD, self.row))
            elif token      == '"'     : self.analyser.append(Token(QUOTE, self.row))
            elif token[0]   == '#'     : self.analyser.append(Token(HEX, self.row, token))
            elif token[0]   == '\n'    : pass 
            elif token.isspace()  : pass
            elif token.isdigit() and token[0] != '0':
                self.analyser.append(Token(token, self.row))
            else:
                self.analyser.append(Token(ERROR, self.row))
                return
            if '\n' in token           : self.row += token.count('\n') # Kollar antalet newlines, läggert till det antalet rader

            
# En klass som analyserar alla tokens
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    # En rekursiv funktion som går igenom alla tokens   
    def program(self):
        prog = None
        if len(self.lexer.analyser) == 0:
            return ExpressionNode(None, None)
        instr = self.instruction()
        
       
        if len(self.lexer.analyser) > 0:
            prog = self.program()
        
        return ExpressionNode(instr, prog)
        
    # En rekursiv funktion som går igenom alla tokens inuti en REP loop
    def rep_program(self):
        prog = None
        if len(self.lexer.analyser) == 0:
            return ExpressionNode(None, None)
        instr = self.instruction()
        
        if len(self.lexer.analyser) > 0 and self.lexer.analyser[0].token != QUOTE:
            prog = self.rep_program()
        
        return ExpressionNode(instr, prog)
   
    # En rekursiv medåkningsfunktion för alla tokens 
    def instruction(self):
        t = self.lexer.analyser[0]
        self.lexer.row = t.row
        t = t.token
        node = None
        if t == FORW or t == BACK or t == LEFT or t == RIGHT:
            return self.moveToken()
        elif t == COLOR:
            return self.colorToken()
        elif t == UP or t == DOWN:
            return self.penToken()
        elif t == REP:
            node = self.repInstr()


        elif t == ERROR:
            print("Syntaxfel på rad " + str(self.lexer.row))
            raise SystemExit()

        else:
            print("Syntaxfel på rad " + str(self.lexer.row))
            raise SystemExit()

        return node


    # En funktion som hanterar PEN tokens (UP och DOWN)
    def penToken(self):

        token = self.lexer.analyser.popleft()
        if len(self.lexer.analyser) == 0:
            print("Syntaxfel på rad " + str(self.lexer.row))
            raise SystemExit()
        end_dot =  self.lexer.analyser.popleft()
        self.lexer.row = end_dot.row
        end_dot_token  = end_dot.token

         # Om vi har inte har en punkt i slutet
        if end_dot_token == PERIOD:
            return PenNode(token)
        else:
            print("Syntaxfel på rad " + str(self.lexer.row))
            raise SystemExit()

    # En funktion som hanterar COLOR tokens        
    def colorToken(self):
        token = self.lexer.analyser.popleft()
        if len(self.lexer.analyser) == 0:
            print("Syntaxfel på rad " + str(token.row))
            raise SystemExit()
        hex = self.lexer.analyser.popleft()
        if len(self.lexer.analyser) == 0:
            print("Syntaxfel på rad " + str(hex.row))
            raise SystemExit()
        
        # Om färgsträngen inte är i rätt format
        if not match(r'#[A-F0-9]{6}',str(hex.value)) or hex.token != HEX:
            print("Syntaxfel på rad " + str(hex.row))
            raise SystemExit()

        end_dot = self.lexer.analyser.popleft()

        # Om vi har inte har en punkt i slutet
        if end_dot.token != PERIOD:
            print("Syntaxfel på rad " + str(end_dot.row))
            raise SystemExit() 
        return ColorNode(hex.value)


    # En funktion som hanterar MOVE tokens (FORW, BACK, LEFT, RIGHT)
    def moveToken(self):
        token = self.lexer.analyser.popleft()
        if len(self.lexer.analyser) == 0:
            print("Syntaxfel på rad " + str(token.row))
            raise SystemExit()
        number = self.lexer.analyser.popleft()
        if len(self.lexer.analyser) == 0:
            print("Syntaxfel på rad " + str(number.row))
            raise SystemExit()
        if not number.token.isdigit():
            print("Syntaxfel på rad " + str(number.row))
            raise SystemExit()

        self.lexer.row = number.row            
        end_dot = self.lexer.analyser.popleft()
        if end_dot.token != PERIOD:
            print("Syntaxfel på rad " + str(end_dot.row))
            raise SystemExit() 
        return MoveNode(token, number.token)

    
    # En funktion som hanterar REP tokens
    def repInstr(self):
        token = self.lexer.analyser.popleft()
        number = self.get_digits(token.value)        

        rep_tokens = None
        if len(self.lexer.analyser) < 2 or not number.isdigit():
            print("Syntaxfel på rad " + str(self.lexer.row))
            raise SystemExit()
        
        if self.lexer.analyser[0].token == QUOTE:
            self.lexer.analyser.popleft()
            self.lexer.row = self.lexer.analyser[0].row

            if self.lexer.analyser[0].token != QUOTE:
                if len(self.lexer.analyser) < 2:
                    print("Syntaxfel på rad " + str(self.lexer.row))
                    raise SystemExit() 
                rep_tokens = self.rep_program()
                if len(self.lexer.analyser) == 0:
                    print("Syntaxfel på rad " + str(self.lexer.row))
                    raise SystemExit()
            self.lexer.row = self.lexer.analyser[0].row
            self.lexer.analyser.popleft()


            if rep_tokens is None or (len(self.lexer.analyser) > 0 and self.lexer.analyser[0] == QUOTE):
                    print("Syntaxfel på rad " + str(self.lexer.row))
                    raise SystemExit()


            
        
        else:
            rep_tokens = self.instruction()
    
        
        return RepNode(number, rep_tokens)
    
    # En funktion som hämtar alla numeriska siffror från en sträng
    def get_digits(self, expr):
        number = ""
        for char in expr:
            if char.isdigit():
                number += char
        return number
    

# Klass som representerar ett syntaxträd
class SyntaxTree(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def process(self, leona):
        pass

# Klass som exekverar alla noder i syntaxträdet
class ExpressionNode(SyntaxTree):
    def __init__(self, instr, prog):
        self.instruction = instr
        self.program = prog

    
    def process(self,leona):
        if not (self.program is None and self.instruction is None):
            
            # Kalla på funktionen rekursivt tills att inte har någon nod kvar 
            if self.program is not None: 
                self.instruction.process(leona)   
                self.program.process(leona)
            else:
                
                # Beroende på vilken nod som läses kallar man då nodklassens process funktion 
                self.instruction.process(leona)



# Nod för MOVE Tokens
class MoveNode(SyntaxTree):
    def __init__(self, token, number):
        self.token = token.token
        self.number = number


    def process(self,leona):
        if self.token == FORW:
            leona.move(self.number)
        if self.token == BACK:
            leona.move(-abs(int(self.number)))   
        elif self.token == LEFT:
            leona.turn(int(self.number))
        elif self.token == RIGHT:
            leona.turn(-abs(int(self.number)))
        

# Nod för PEN Tokens
class PenNode(SyntaxTree):
    def __init__(self, token):
        self.token = token.token 
    def process(self,leona):
        if self.token == DOWN:
            leona.pen = True
        else:
            leona.pen = False

# Nod för COLOR Tokens
class ColorNode(SyntaxTree):
    def __init__(self, color):
        self.color = color
    
    def process(self,leona):
        leona.color = self.color


# Nod för REP Tokens
class RepNode(SyntaxTree):
    def __init__(self, number, expr):
        self.number = number
        self.expression = expr
        self.rep = True
    
    def process(self,leona):
        for i in range(int(self.number)):
            self.expression.process(leona)
                
       



# Klass som representerar         
class Leona:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.prev_x = 0
        self.prev_y = 0
        self.angle = 0
        self.color = "#0000FF"
        self.pen = False
        self.current_row = 1
        self.print_instructions = []
    
    
    def move(self, steps):
        self.x += float(steps) * float(cos((pi * self.angle) / 180))
        self.y += float(steps) * float(sin((pi * self.angle) / 180))

        if self.pen is True:
           output = [self.color, str("{:.4f}".format(self.prev_x)), str("{:.4f}".format(self.prev_y)), str("{:.4f}".format(self.x)),str("{:.4f}".format(self.y))]
           
           # Sparar alla print instructions i en lista 
           self.print_instructions.append(output)

        self.prev_x = self.x
        self.prev_y = self.y


    def turn(self, turn_angle):
        self.angle += turn_angle

    


def main():

    expr = ""
    input_list = ""
    leona = Leona()

    # Hämtar input sträng
    for i in stdin:
        # if i == "\n":
        #     break
        expr += str(i)
        

    # Ta bort alla kommentarer och ersätter med newline för att förenkla till LexAnalysatorn
    input_list =  sub('%.*\n?', '\n', expr.upper())


    # För samman relevanta delar av input strängen till ett och samma listlelement, resten blir individuella element i den nyskapade listan
    input_list = findall('\s+|\.|\d+|\"|FORW\s|BACK\s|LEFT\s|RIGHT\s|COLOR\s|UP|DOWN|#[A-Fa-f0-9]{6}|REP\s+[1-9]\d*\s+|.', input_list) # Ta bort %.*\n
    # Lexikal analysator
    lexer = LexAnalysator(input_list)
    lexer.add_tokens(input_list)
    
    # Parsning
    main_parser = Parser(lexer)
    res = main_parser.program()
    
    # Exekvering
    res.process(leona)
    # Printar ut alla print instructions när Leona rör sig framåt eller bak
    print('\n'.join(' '.join(map(str, sub)) for sub in leona.print_instructions))


if __name__ == "__main__":
    main()



