import random

class CodeGenerator:    

    def __init__(self, alphabet: str):

        self.__alphabet = alphabet

    def generate_code(self, length=5):

        return str().join(random.choice(self.__alphabet) for _ in range(length))
