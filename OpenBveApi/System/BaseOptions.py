from abc import ABC, abstractmethod

class BaseOptions(ABC):
    def __init__(self):
        self.EnableBveTsHacks = False
