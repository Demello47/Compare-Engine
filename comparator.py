from difflib import SequenceMatcher


def length_is_reasonable(text_a, text_b, config):
    len_a = len(text_a)
    len_b = len(text_b)

    if len_a == 0 or len_b == 0:
        return False

    ratio = min(len_a, len_b) / max(len_a, len_b)

    return ratio >= config["min_length_ratio"]


def similarity(text_a, text_b):
    matcher = SequenceMatcher(
        None,
        text_a,
        text_b,
        autojunk=True
    )

    quick = matcher.quick_ratio()

    return quick, matcher


def make_result(
    result_type,
    line_a=None,
    line_b=None,
    node_a=None,
    node_b=None
):
    return {
        "type": result_type,
        "line_a": line_a,
        "line_b": line_b,
        "node_a": node_a,
        "node_b": node_b,
    }


def pair_changed_lines(lines_a, lines_b, config):
    results = []

    used_b = set()

    for index_a, line_a in enumerate(lines_a):
        text_a = line_a["normalized"]

        best_index = None
        best_ratio = 0.0

        start = max(
            0,
            index_a - config["change_window"]
        )

        end = min(
            len(lines_b),
            index_a + config["change_window"] + 1
        )

        for index_b in range(start, end):
            if index_b in used_b:
                continue

            line_b = lines_b[index_b]
            text_b = line_b["normalized"]

            if not length_is_reasonable(
                text_a,
                text_b,
                config
            ):
                continue

            quick_ratio, matcher = similarity(
                text_a,
                text_b
            )

            if quick_ratio < config["change_threshold"]:
                continue

            ratio = matcher.ratio()

            if ratio > best_ratio:
                best_ratio = ratio
                best_index = index_b

        if (
            best_index is not None
            and best_ratio >= config["change_threshold"]
        ):
            used_b.add(best_index)

            results.append(
                make_result(
                    "CHANGED",
                    line_a=line_a,
                    line_b=lines_b[best_index]
                )
            )
        else:
            results.append(
                make_result(
                    "REMOVED",
                    line_a=line_a
                )
            )

    for index_b, line_b in enumerate(lines_b):
        if index_b not in used_b:
            results.append(
                make_result(
                    "ADDED",
                    line_b=line_b
                )
            )

    return results


def compare_line_lists(lines_a, lines_b, config):
    texts_a = [
        line["normalized"]
        for line in lines_a
    ]

    texts_b = [
        line["normalized"]
        for line in lines_b
    ]

    matcher = SequenceMatcher(
        None,
        texts_a,
        texts_b,
        autojunk=True
    )

    results = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                results.append(
                    make_result(
                        "SAME",
                        line_a=lines_a[i1 + offset],
                        line_b=lines_b[j1 + offset]
                    )
                )

        elif tag == "delete":
            for line_a in lines_a[i1:i2]:
                results.append(
                    make_result(
                        "REMOVED",
                        line_a=line_a
                    )
                )

        elif tag == "insert":
            for line_b in lines_b[j1:j2]:
                results.append(
                    make_result(
                        "ADDED",
                        line_b=line_b
                    )
                )

        elif tag == "replace":
            results.extend(
                pair_changed_lines(
                    lines_a[i1:i2],
                    lines_b[j1:j2],
                    config
                )
            )

    return results


def build_comparisons(
    aligned_blocks,
    file_a,
    file_b,
    config
):
    comparisons = []

    for pair in aligned_blocks:
        block_a = pair["block_a"]
        block_b = pair["block_b"]
        status = pair["status"]

        node_a = (
            block_a["node_name"]
            if block_a is not None
            else None
        )

        node_b = (
            block_b["node_name"]
            if block_b is not None
            else None
        )

        if status == "MATCHED":
            results = compare_line_lists(
                block_a["lines"],
                block_b["lines"],
                config
            )

        elif status == "A_ONLY":
            results = [
                make_result(
                    "REMOVED",
                    line_a=line,
                    node_a=node_a
                )
                for line in block_a["lines"]
            ]

        elif status == "B_ONLY":
            results = [
                make_result(
                    "ADDED",
                    line_b=line,
                    node_b=node_b
                )
                for line in block_b["lines"]
            ]

        else:
            results = compare_line_lists(
                block_a["lines"],
                block_b["lines"],
                config
            )

        for result in results:
            result["node_a"] = node_a
            result["node_b"] = node_b
            result["block_status"] = status
            result["file_a"] = file_a
            result["file_b"] = file_b

        comparisons.extend(results)

    return comparisons


def calculate_statistics(results):
    statistics = {
        "TOTAL": 0,
        "SAME": 0,
        "CHANGED": 0,
        "ADDED": 0,
        "REMOVED": 0,
    }

    for result in results:
        result_type = result["type"]

        statistics["TOTAL"] += 1

        if result_type in statistics:
            statistics[result_type] += 1

    return statistics