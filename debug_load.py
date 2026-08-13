from file_manager import FileManager
loaded = FileManager.load_assignments()
print('Loaded count =', len(loaded))
for idx,a in enumerate(loaded,1):
    print(idx, type(a).__name__, getattr(a,'title',None), getattr(a,'subject',None))
