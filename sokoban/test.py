from pyinstrument import Profiler
import time

def slow():
    for _ in range(3):
        time.sleep(0.5)

if __name__ == '__main__':
    profiler = Profiler()
    profiler.start()

    slow()

    profiler.stop()
    print(profiler.output_text(unicode=True, color=True))