import re


TIMESTAMP_PATTERN = re.compile(
    r"\b"
    r"\d{4}-\d{2}-\d{2}"
    r"\s+"
    r"\d{2}:\d{2}:\d{2}"
    r"(?:[,.]\d+)?"
    r"\b"
)


def remove_timestamp(text):
    return TIMESTAMP_PATTERN.sub("", text)


def remove_first_columns(text, count):
    parts = text.split()

    if len(parts) <= count:
        return text.strip()

    return " ".join(parts[count:])


def normalize_whitespace(text):
    return " ".join(text.split())


def normalize_line(line, config):
    text = line.rstrip("\r\n")

    if config["remove_timestamps"]:
        text = remove_timestamp(text)

    text = remove_first_columns(
        text,
        config["ignore_first_columns"]
    )

    text = normalize_whitespace(text)

    return text