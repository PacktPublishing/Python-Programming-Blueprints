class Mapper:

    def __init__(self):
        self._mapping = {}

    def _add(self, source, dest):
        self._mapping[source] = dest

    def remap_key(self, source, dest):
        self._add(source, dest)

    def remap(self, itemslist):
        return [self._exec(item) for item in itemslist]

    def _exec(self, src_dict):
        dest = dict()

        if not src_dict:
            raise AttributeError('The source dictionary can be empty or None')

        for key, value in src_dict.items():
            try:
                new_key = self._mapping[key]
                dest[new_key] = value
            except KeyError:
                dest[key] = value
        return dest