from uuid import uuid1


class MenuItem:
    def __init__(self, label, data, selected=False):
        self.id = str(uuid1())
        self.data = data
        self.label = label

        def return_id():
            return self.data['id'], self.data['uri']

        self.action = return_id
        self.selected = selected

    def __eq__(self, other):
        return self.id == other.id

    def __len__(self):
        return len(self.label)

    def __str__(self):
        return self.label