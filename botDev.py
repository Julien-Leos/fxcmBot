import sys
from dev.Session import Session
from dev.Loader import Loader

s = Session()
l = Loader()
l.load("bot", ["utils", "algorithm", "fxcm"])

active = True

while active:
    try:
        while input("Press 'return' to start the bot...") != '': continue
        l.run(s, sys.argv)

    except EOFError:
        print("\nClosing connection")
        s.close()
        active = False
        continue
