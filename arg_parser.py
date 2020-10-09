class SimpleArgParser:

    def __init__(self, args):
        self.parsed = {}
        for i, a in enumerate(args):
            parts = a.split("=")
            if len(parts) == 1:
                self.parsed[f"#{i}"] = parts[0]
            elif len(parts) == 2:
                self.parsed[parts[0]] = parts[1]
        print(self.parsed)

    def find_arg(self, position):
        val = self.parsed.get(f"#{position}")
        if val is None:
            raise Exception("Unable to find argument at:", position)
        return val

    def find_arg_by_name(self, name, default=None):
        val = self.parsed.get(name)
        if val is not None:
            return val
        if default is not None:
            return default
        raise Exception("Unable to find argument named:", name)
