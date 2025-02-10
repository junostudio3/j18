from jconsole.parser import JConsoleParser as jCP


class ConsolePorgress:
    def __init__(self, is_download: bool):
        self.is_download = is_download
        self.max_charector_count = 40
        self.pos = 0
        self.update_line_by_step = False

    def set_startsummary(self, total_size):
        if self.is_download:
            jCP.println(f"download total data size = {total_size}")
        else:
            jCP.println(f"upload total data size = {total_size}")

    def start(self, file_name, total_size):
        self.total_size = total_size
        self.file_name = file_name
        self.pos = 0
        self.progress_pos = 0
        self.__display_progress()

    def proc(self, pos):
        old_progress = self.progress_pos
        self.update_pos(pos)
        if old_progress == self.progress_pos:
            return    # 너무 자주 갱신하지 말자. 깜빡거려서 보기 안 좋을 수 있으므로 #

        if self.update_line_by_step is False:
            jCP.print('\r')

        self.pos = pos
        self.__display_progress()

    def end(self):
        if self.update_line_by_step is False:
            jCP.print('\r')

        self.update_pos(self.total_size)
        self.__display_progress()

        if self.update_line_by_step is False:
            jCP.println()

    def update_pos(self, pos):
        self.pos = pos
        self.progress_pos = 0
        if self.total_size <= 0:
            # totalSize가 0이면 progressPos를 계산할 수 없다.
            return

        self.progress_pos = int(self.pos *
                                self.max_charector_count / self.total_size)

    def __display_progress(self):
        jCP.print('[')

        for i in range(self.max_charector_count):
            if i < self.progress_pos:
                jCP.print('=')
            else:
                jCP.print(' ')

        percent = self.pos * 100.00 / self.total_size
        jCP.print(f'] {percent:.2f}%% ({self.pos} / {self.total_size}) ' +
                  self.file_name)

        if self.update_line_by_step:
            jCP.println()
