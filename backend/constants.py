from enum import Enum, auto

class Schedule(Enum):
    EVERYDAY = auto()
    PROBING = auto()
    CUSTOM = auto()

if __name__ == '__main__':
    print(1 in Schedule)
    print(3 in Schedule)
    print(4 in Schedule)
