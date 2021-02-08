from subprocess import Popen, PIPE
import os

for item in os.listdir(os.getcwd()):
    if os.path.isfile(item):
        if os.path.splitext(item)[1] == ".py":
            process = Popen(["python", "-m", "pyflakes", item],
                            bufsize=20, stdout=PIPE, stderr=PIPE)
            for line in iter(process.stdout.readline, b""):
                line = line.decode("utf-8")
                print(line)
