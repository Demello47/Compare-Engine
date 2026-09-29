from pathlib import Path


def create_rule_file(file_path):
    path = Path(file_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if not path.exists():
        path.touch()


def load_rules(file_path):
    create_rule_file(file_path)

    path = Path(file_path)

    rules = []

    with path.open(
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:
        for line in file:
            rule = line.strip()

            if rule:
                rules.append(rule)

    return rules


def matches_rule(text, rules, ignore_case=True):
    if not text:
        return False

    if ignore_case:
        text = text.lower()

    for rule in rules:
        check_rule = (
            rule.lower()
            if ignore_case
            else rule
        )

        if check_rule in text:
            return True

    return False


def get_result_texts(result):
    texts = []

    line_a = result.get("line_a")
    line_b = result.get("line_b")

    if line_a:
        texts.extend([
            line_a.get("original", ""),
            line_a.get("normalized", ""),
            line_a.get("display", ""),
        ])

    if line_b:
        texts.extend([
            line_b.get("original", ""),
            line_b.get("normalized", ""),
            line_b.get("display", ""),
        ])

    return [
        text
        for text in texts
        if text
    ]


def result_matches_rules(
    result,
    rules,
    config
):
    texts = get_result_texts(result)

    for text in texts:
        if matches_rule(
            text,
            rules,
            config["rules_ignore_case"]
        ):
            return True

    return False


def filter_results(
    results,
    keywords,
    excludes,
    config
):
    filtered = []

    for result in results:
        if result_matches_rules(
            result,
            excludes,
            config
        ):
            continue

        result["keyword"] = result_matches_rules(
            result,
            keywords,
            config
        )

        if (
            result["type"] == "SAME"
            and not config["show_same"]
            and not result["keyword"]
        ):
            continue

        filtered.append(result)

    return filtered