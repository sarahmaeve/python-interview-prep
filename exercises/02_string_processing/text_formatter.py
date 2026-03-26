def title_case(text):
    """Convert text to title case (capitalize the first letter of each word)."""
    if not text:
        return text
    result = text.lower()
    output = list(result)
    for i in range(len(output)):
        if i > 0 and output[i - 1] == " ":
            output[i] = output[i].upper()
    return "".join(output)


def truncate(text, max_length):
    """Truncate text to max_length characters, adding '...' if truncated.

    The returned string (including the '...' suffix) must not exceed
    max_length.  Truncation happens at a character boundary, not a word
    boundary.  If the text fits within max_length, return it unchanged.
    """
    if len(text) <= max_length:
        return text
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
            current_line = " " + word

    lines.append(current_line)
    return "\n".join(lines)
