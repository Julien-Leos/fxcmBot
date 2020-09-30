from importlib import reload


class Loader():
    botModuleFiles = list()

    def __init__(self, file=None):
        self.__file__ = file
        if file != None:
            self.__mod__ = __import__(file)

    def __currentFile__(self):
        return self.__file__

    def __load__(self, givenFile=None):
        if givenFile != None:
            self.__file__ = givenFile
        if givenFile == None and self.__file__ == None:
            raise Exception("No file name given")
        try:
            if givenFile == None:
                print("Reloading module")
                self.__mod__ = reload(self.__file__)
            else:
                print("Loading new one")
                self.__file__ = givenFile
                self.__mod__ = __import__(givenFile)
        except Exception as e:
            print("Fuck : ", e)

    def load(self, botFilename, botModuleFilenames):
        self.botFile = __import__(botFilename)
        for botModuleFilename in botModuleFilenames:
            self.botModuleFiles.append(__import__(botModuleFilename))

    def run(self, session):
        for botModuleFile in self.botModuleFiles:
            reload(botModuleFile)
        self.botFile = reload(self.botFile)

        try:
            getattr(self.botFile, "mainDev")(session.getConnection())
            print("Press 'Crtl-D' to close the programm")
        except Exception as e:
            print("Could not run function : ", e)
