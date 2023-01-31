from os import walk
import pathlib

_path = pathlib.Path(__file__).parent.resolve()

print(_path)

f = []
for _, _, filenames in walk(_path):
    f.extend(filenames)
    print(filenames)
    break
