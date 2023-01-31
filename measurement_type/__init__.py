# from os import walk
# import pathlib

# _path = pathlib.Path(__file__).parent.resolve()
# modules = []
# for _, _, filenames in walk(_path):
#     for file in filenames:
#         if len(file) >= 3:
#             if file[-3:] == ".py" and file[:-3] != "__init__":
#                 modules.append(file)
#                 print(file[:-3])

# __all__ = modules
