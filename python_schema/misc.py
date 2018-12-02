from . import exception


class ValueNotSet:
    is_set = False

    def __str__(self):
        return "NotSet"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, value):
        try:
            if isinstance(self, value):
                return True
        except TypeError:
            pass

        raise exception.ValueNotSetError(
            "Value on field was not set, thus comparison will always fail")
