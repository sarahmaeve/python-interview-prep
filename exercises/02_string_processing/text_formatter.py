def title_case(text):
    """Convert text to title case (capitalize the first letter of each word)."""
    if not text:
        return text
    result = text.lower()
    # BUG: only capitalizes characters after spaces, misses the first character
    output = list(result)
    for i in range(len(output)):
        if i > 0 and output[i - 1] == " ":
            output[i] = output[i].upper()
    return "".join(output)


def truncate(text, max_length):
    """Truncate text to max_length, adding '...' if truncated."""
    if len(text) <= max_length:
        return text
    # BUG: doesn't account for the length of "..." — result exceeds max_length
    return text[:max_length] + "..."


def word_wrap(text, width):
    """Wrap text to the given width, breaking at spaces."""
    words = text.split(" ")
    lines = []
    current_line = words[0]

    for word in words[1:]:
        if len(current_line) + 1 + len(word) <= width:
            current_line += " " + word
        else:
            lines.append(current_line)
            # BUG: should be just `word`, but prepends a space
            current_line = " " + word

    lines.append(current_line)
    return "\n".join(lines)
