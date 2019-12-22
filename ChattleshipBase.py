class CLI: #Do not initiate this class!
    def input(why):
        if why == "attempt-attack":
            valid = False
            while not valid:
                tmp = input("Cell to attack: ").upper()
                try:
                    letter, number = tmp[0], int(tmp[1:])
                    assert letter in "ABCDEFGHIJ"
                    assert number in range(1, 11)
                    valid = True
                except:
                    print("Invalid cell %s. Please try again." % tmp)
            return tmp
        elif why == "answer-defend":
            valid = False
            while not valid:
                tmp = input("Result of attack: ").upper()
                try:
                    assert tmp in ["MISS", "HIT", "SUNKEN SHIP", "YOU WIN"]
                    valid = True
                except:
                    print('Invalid answer. Must be "MISS", "HIT", "SUNKEN SHIP", or "YOU WIN"')
            return tmp
    def output(x, why):
        if why == "answer-attack":
            print("Result: %s" % x)
        elif why == "attempt-defend":
            print("Opponent attacked %s" % x)
            

class Base:
    def __init__(self, chat, ui):
        self.chat = chat
        self.ui = ui
        
    def play(self, isFirst):
        gameOver = False
        if isFirst:
            self.attack()
        while not gameOver:
            if self.defend(): return
            if self.attack(): return
        
    def attack(self):
        self.chat[1](self.ui[0](why="attempt-attack"))
        tmp = self.chat[0]()
        self.ui[1](tmp, why="answer-attack")
        return tmp == "YOU WIN"
        
    def defend(self):
        self.ui[1](self.chat[0](), why="attempt-defend")
        tmp = self.ui[0](why="answer-defend")
        self.chat[1](tmp)
        return tmp == "YOU WIN"
        
if __name__ == "__main__":
    inst = Base(
        [
            (lambda: input("CHAT IN: ")),
            (lambda x: print("CHAT OUT: %s" % x))
        ],
##        [
##            (lambda why: input("UI IN because of %s: " % why)),
##            (lambda x, why: print("UI OUT because of %s: %s" % (why, x)))
##        ]
        [CLI.input, CLI.output]
    )
    inst.play(input("Is first? (Y/n) ").lower().startswith("y"))
