from srcDev.Session import Session
from srcDev.Loader import Loader

s = Session()
l = Loader()
l.load("bot", ["src.fxcm", "src.utils", "src.algorithm"])

active = True

while active:
    try:
        input("Press 'return' to start the bot...")
        l.run(s)

    except EOFError:
        print("\nClosing connection")
        s.close()
        active = False
        continue
