import random


class Utils:
    def createRandomString(self):
        characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        return "".join(random.choice(characters) for i in range(8))

    def createRandomId(self):
        characters = "1234567890"
        return "".join(random.choice(characters) for i in range(4))
