class ChoicesStringsMixin:
    @classmethod
    def choices(cls):
        return [(choice.value, choice.value) for choice in cls]

    @classmethod
    def max_len(cls):
        return max(len(name) for name, _ in cls.choices())
