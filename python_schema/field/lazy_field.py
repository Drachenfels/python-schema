import importlib


class LazyField:
    def __init__(self, name, load, **kwargs):
        """LazyField allows as name suggest lazy load any other class. Usefull
        in cases where we would be victims of cyclic import or using declared
        class as child field.

        name :: name that should be given to lazy loaded class, almost all
            other classes in python schema require name so this one is
            mandatory as well

        load :: what to load, it should be string that is an importable python
            module that ends up with a class that we are intersted in, example
            would be `tests.test_schema_field.MyClass`

        kwargs :: any attribute that lazy loaded class is accepting and that
            will be passed on field resolution
        """
        self.name = name
        self.load = load
        self.kwargs = kwargs

    def make_new(self):
        """Execute lazy-load.
        """
        name = self.load.split('.')[-1]
        path = self.load[:(len(name) + 1) * -1]

        module = importlib.import_module(path)

        new_class = getattr(module, name)

        return new_class(name=self.name, **self.kwargs)
