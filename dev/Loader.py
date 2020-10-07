from importlib import reload


class Loader():
    botModuleFiles = list()

    def load(self, botFilename, botModuleFilenames):
        self.botFile = __import__(botFilename)
        for botModuleFilename in botModuleFilenames:
            self.botModuleFiles.append(__import__(botModuleFilename))

    def run(self, session, argv):
        for botModuleFile in self.botModuleFiles:
            reload(botModuleFile)
        self.botFile = reload(self.botFile)

        try:
            getattr(self.botFile, "mainDev")(session.getConnection(), argv)
            print("\nPress 'Crtl-D' to close the programm")
        except Exception as e:
            print("Could not run function : ", e)
