import time


class ProgressBar:
    def __init__(self, width=20, total=100, info="正在爆破"):
        self.width = width
        self.total = total
        self.progress = 0

        self.finished = False

        self.info = info

    def reset(self):
        self.progress = 0
        self.finished = False

    def set_info(self, info):
        self.info = info
        self.__update()

    def set_progress(self, progress):
        self.progress = progress
        self.__update()

    def work(self, n):
        self.progress += n
        if self.progress > self.total:
            self.progress = self.total
        self.__update()

    def __update(self):
        if not self.finished:
            percent = self.progress / self.total

            filled_width = int(self.width * percent)
            empty_width = self.width - filled_width

            print(
                f"{self.info}: [{'=' * filled_width}{' ' * empty_width}]\t{percent*100:.2f}%\t{self.progress}/{self.total}\t\r",
                end="",
            )

            if self.progress >= self.total:
                self.finished = True
                print()


if __name__ == "__main__":
    import random

    bar = ProgressBar(total=239080821)
    while True:
        time.sleep(0.01)
        bar.work(random.randint(1, 1000))
        if bar.finished:
            break
