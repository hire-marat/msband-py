def process_cs_int_enum(input: str):
    current = 0
    mapping = {}

    for declaration in input.split("\r\n"):
        declaration = declaration.strip().rstrip(",")
        split = declaration.split(" = ", 1)
        if len(split) == 1:
            (name,) = split
        else:
            name, value = split
            current = int(value)

        mapping[name] = current
        current += 1

    return """class NewEnum(enum.IntEnum):\n""" + "\n".join(
        f"    {name} = {value:02X}" for name, value in mapping.items()
    )
