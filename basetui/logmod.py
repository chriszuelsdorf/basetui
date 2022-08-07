import os
from datetime import datetime


class logbuf:
    valid_levels = [0, 1, 2, 3]

    def __init__(self, file, filter=2):
        """Init

        Args:
            file (str): The filepath to use. Will be deleted during init.
            filter (int, optional): Minimum message priority to log; 0 is Debug, 3 is High. Defaults to 2.
        """
        if filter not in self.valid_levels:
            raise ValueError(f"Expected priority filter, got {filter}")
        self.filter = filter
        self.file = file
        if os.path.isdir(file):
            raise IsADirectoryError
        with open(file, mode="w") as f:
            ...
        self.buffer = []

    def log(self, text, priority=2):
        if priority not in self.valid_levels:
            raise ValueError(f"Expected priority, got {priority}")
        if priority >= self.filter:
            self.buffer.append(str(datetime.now()) + " -> " + str(text))
        if len(self.buffer) >= 100:
            self.flush()

    def flush(self) -> None:
        self.buffer.append(str(datetime.now()) + " -> LOGBUF <> Flushed Log Buffer")
        with open(self.file, mode="a") as f:
            for l in self.buffer:
                if l.endswith("\n"):
                    f.write(l)
                else:
                    f.write(l + "\n")
        self.buffer = []
