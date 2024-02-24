SPECIAL_CHARS = "`\\\"'*~_"

def escape_special_chars(input: str) -> str:
    global SPECIAL_CHARS

    if not isinstance(input, str):
        raise ValueError
    
    i = 0
    output_str = ""
    while i < len(input):
        if input[i] in SPECIAL_CHARS:
            output_str += "\\"
        output_str += input[i]
        i+=1
    return output_str