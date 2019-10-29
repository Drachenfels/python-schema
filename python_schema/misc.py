import importlib


class NotSet:
    pass


class ImportModule:
    def __init__(self, path_to_class):
        self.class_name = path_to_class.split('.')[-1]
        self.path_to_module = path_to_class[:(len(self.class_name) + 1) * -1]

    def get_class(self):
        """Methods attempt to import class from module and returns instance of
        the imported class"""
        module = importlib.import_module(self.path_to_module)

        return getattr(module, self.class_name)
