
def parse_number(const: str) -> int | None:
    if const.startswith("$"):
        try:
            return int(const[1:], 16)
        except ValueError:
            return None
    elif const.startswith("%"):
        try:
            return int(const[1:], 2)
        except ValueError:
            return None
    else:
        try:
            return int(const)
        except ValueError:
            return None
