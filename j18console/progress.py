from jconsole.parser import jConsoleParser as jCP


class ConsolePorgress:
    def __init__(self, isDownload: bool):
        self.isDownload = isDownload
        self.maxCharectorCount = 40
        self.pos = 0
        self.updateLineByStep = False

    def SetStartSummary(self, totalSize):
        if self.isDownload:
            jCP.PrintLn(f"download total data size = {totalSize}")
        else:
            jCP.PrintLn(f"upload total data size = {totalSize}")

    def Start(self, fileName, totalSize):
        self.totalSize = totalSize
        self.fileName = fileName
        self.pos = 0
        self.progressPos = 0
        self.__DisplayProgress()

    def Proc(self, pos):
        oldProgress = self.progressPos
        self.UpdatePos(pos)
        if oldProgress == self.progressPos:
            return    # 너무 자주 갱신하지 말자. 깜빡거려서 보기 안 좋을 수 있으므로 #

        if self.updateLineByStep is False:
            jCP.Print('\r')

        self.pos = pos
        self.__DisplayProgress()

    def End(self):
        if self.updateLineByStep is False:
            jCP.Print('\r')

        self.UpdatePos(self.totalSize)
        self.__DisplayProgress()

        if self.updateLineByStep is False:
            jCP.PrintLn()

    def UpdatePos(self, pos):
        self.pos = pos
        self.progressPos = 0
        if self.totalSize <= 0:
            # totalSize가 0이면 progressPos를 계산할 수 없다.
            return

        self.progressPos = int(self.pos *
                               self.maxCharectorCount / self.totalSize)

    def __DisplayProgress(self):
        jCP.Print('[')

        for i in range(self.maxCharectorCount):
            if i < self.progressPos:
                jCP.Print('=')
            else:
                jCP.Print(' ')

        percent = self.pos * 100.00 / self.totalSize
        jCP.Print(f'] {percent:.2f}%% ({self.pos} / {self.totalSize}) ' +
                  self.fileName)

        if self.updateLineByStep:
            jCP.PrintLn()
