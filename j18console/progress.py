from jconsole.parser import jConsoleParser as jCP


class ConsolePorgress:
    def __init__(self, is_download: bool):
        self.is_download = is_download
        self.max_charector_count = 40
        self.pos = 0
        self.update_line_by_step = False

    def SetStartSummary(self, total_size):
        if self.is_download:
            jCP.PrintLn(f"download total data size = {total_size}")
        else:
            jCP.PrintLn(f"upload total data size = {total_size}")

    def Start(self, file_name, total_size):
        self.total_size = total_size
        self.file_name = file_name
        self.pos = 0
        self.progress_pos = 0
        self.__DisplayProgress()

    def Proc(self, pos):
        old_progress = self.progress_pos
        self.UpdatePos(pos)
        if old_progress == self.progress_pos:
            return    # 너무 자주 갱신하지 말자. 깜빡거려서 보기 안 좋을 수 있으므로 #

        if self.update_line_by_step is False:
            jCP.Print('\r')

        self.pos = pos
        self.__DisplayProgress()

    def End(self):
        if self.update_line_by_step is False:
            jCP.Print('\r')

        self.UpdatePos(self.total_size)
        self.__DisplayProgress()

        if self.update_line_by_step is False:
            jCP.PrintLn()

    def UpdatePos(self, pos):
        self.pos = pos
        self.progress_pos = 0
        if self.total_size <= 0:
            # totalSize가 0이면 progressPos를 계산할 수 없다.
            return

        self.progress_pos = int(self.pos *
                                self.max_charector_count / self.total_size)

    def __DisplayProgress(self):
        jCP.Print('[')

        for i in range(self.max_charector_count):
            if i < self.progress_pos:
                jCP.Print('=')
            else:
                jCP.Print(' ')

        percent = self.pos * 100.00 / self.total_size
        jCP.Print(f'] {percent:.2f}%% ({self.pos} / {self.total_size}) ' +
                  self.file_name)

        if self.update_line_by_step:
            jCP.PrintLn()
