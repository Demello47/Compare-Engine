from difflib import SequenceMatcher
from html import escape
from pathlib import Path


def get_line_text(line):
    if not line:
        return ""

    return line.get(
        "display",
        line.get("normalized", "")
    )


def get_line_number(line):
    if not line:
        return "-"

    return line.get("line_number", "-")


def create_difference_markers(text_a, text_b, marker="^"):
    matcher = SequenceMatcher(
        None,
        text_a,
        text_b,
        autojunk=False
    )

    marker_a = [" "] * len(text_a)
    marker_b = [" "] * len(text_b)

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue

        if tag in ("replace", "delete"):
            for index in range(i1, i2):
                marker_a[index] = marker

        if tag in ("replace", "insert"):
            for index in range(j1, j2):
                marker_b[index] = marker

    return "".join(marker_a), "".join(marker_b)


def html_diff(text_a, text_b):
    matcher = SequenceMatcher(
        None,
        text_a,
        text_b,
        autojunk=False
    )

    html_a = []
    html_b = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        part_a = escape(text_a[i1:i2])
        part_b = escape(text_b[j1:j2])

        if tag == "equal":
            html_a.append(part_a)
            html_b.append(part_b)

        elif tag == "replace":
            html_a.append(
                f'<span class="char-diff">{part_a}</span>'
            )
            html_b.append(
                f'<span class="char-diff">{part_b}</span>'
            )

        elif tag == "delete":
            html_a.append(
                f'<span class="char-diff">{part_a}</span>'
            )

        elif tag == "insert":
            html_b.append(
                f'<span class="char-diff">{part_b}</span>'
            )

    return "".join(html_a), "".join(html_b)


def get_node_title(result):
    node_a = result.get("node_a")
    node_b = result.get("node_b")

    if node_a and node_b:
        if node_a == node_b:
            return node_a

        return f"{node_a}  <->  {node_b}"

    if node_a:
        return f"{node_a}  <->  [NONE]"

    if node_b:
        return f"[NONE]  <->  {node_b}"

    return "[NO NODE]"


def write_statistics_text(file, statistics):
    file.write("\n")
    file.write("=" * 80 + "\n")
    file.write("SUMMARY\n")
    file.write("=" * 80 + "\n")

    for name in (
        "TOTAL",
        "SAME",
        "CHANGED",
        "ADDED",
        "REMOVED",
    ):
        file.write(
            f"{name}: {statistics.get(name, 0):,}\n"
        )


def write_text_report(
    results,
    statistics,
    file_a,
    file_b,
    config
):
    output_path = Path(config["text_report"])

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        file.write(f"FILE A: {file_a}\n")
        file.write(f"FILE B: {file_b}\n")
        file.write("=" * 80 + "\n")

        current_node = None

        for result in results:
            node_title = get_node_title(result)

            if node_title != current_node:
                current_node = node_title

                file.write("\n")
                file.write("=" * 80 + "\n")
                file.write(
                    f"NODE: {node_title}\n"
                )
                file.write("=" * 80 + "\n")

            result_type = result["type"]

            if result.get("keyword"):
                label = "[KEYWORD]"
            else:
                label = f"[{result_type}]"

            line_a = result.get("line_a")
            line_b = result.get("line_b")

            text_a = get_line_text(line_a)
            text_b = get_line_text(line_b)

            number_a = get_line_number(line_a)
            number_b = get_line_number(line_b)

            if result_type == "SAME":
                file.write(
                    f"{label} "
                    f"{Path(file_a).name}:{number_a} "
                    f"{text_a}\n"
                )

            elif result_type == "REMOVED":
                file.write(
                    f"{label} "
                    f"{Path(file_a).name}:{number_a} "
                    f"{text_a}\n"
                )

            elif result_type == "ADDED":
                file.write(
                    f"{label} "
                    f"{Path(file_b).name}:{number_b} "
                    f"{text_b}\n"
                )

            elif result_type == "CHANGED":
                file.write(
                    f"{label} "
                    f"{Path(file_a).name}:{number_a} "
                    f"{text_a}\n"
                )

                file.write(
                    f"{label} "
                    f"{Path(file_b).name}:{number_b} "
                    f"{text_b}\n"
                )

                if config["mark_changed_differences"]:
                    marker_a, marker_b = (
                        create_difference_markers(
                            text_a,
                            text_b,
                            config["difference_marker"]
                        )
                    )

                    file.write(
                        f"         {marker_a}\n"
                    )
                    file.write(
                        f"         {marker_b}\n"
                    )

        write_statistics_text(
            file,
            statistics
        )


def html_header(file_a, file_b):
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Log Comparison</title>
<style>
body {{
    background: #111;
    color: #ddd;
    font-family: Consolas, monospace;
    margin: 20px;
}}

h1 {{
    color: #fff;
}}

.files {{
    margin-bottom: 20px;
}}

.file-a {{
    color: #55c7ff;
}}

.file-b {{
    color: #d48cff;
}}

.node {{
    background: #222;
    border-left: 5px solid #888;
    padding: 10px;
    margin-top: 25px;
    font-weight: bold;
    font-size: 16px;
}}

.row {{
    padding: 5px 8px;
    margin: 2px 0;
    white-space: pre-wrap;
    word-break: break-word;
}}

.same {{
    color: #aaa;
}}

.changed {{
    background: #4b351c;
}}

.added {{
    background: #173c24;
}}

.removed {{
    background: #4a1d1d;
}}

.keyword {{
    background: #142d4c;
}}

.char-diff {{
    color: #ff5c5c;
    font-weight: bold;
    text-decoration: underline;
}}

.label {{
    display: inline-block;
    width: 95px;
    font-weight: bold;
}}

.line-number {{
    display: inline-block;
    width: 90px;
}}

.summary {{
    margin-top: 30px;
    padding: 15px;
    background: #222;
}}

.summary div {{
    margin: 4px 0;
}}
</style>
</head>
<body>

<h1>Log Comparison</h1>

<div class="files">
    <div class="file-a">FILE A: {escape(str(file_a))}</div>
    <div class="file-b">FILE B: {escape(str(file_b))}</div>
</div>
"""


def write_html_report(
    results,
    statistics,
    file_a,
    file_b,
    config
):
    output_path = Path(config["html_report"])

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        file.write(
            html_header(
                file_a,
                file_b
            )
        )

        current_node = None

        for result in results:
            node_title = get_node_title(result)

            if node_title != current_node:
                current_node = node_title

                file.write(
                    f'<div class="node">'
                    f'NODE: {escape(node_title)}'
                    f'</div>\n'
                )

            result_type = result["type"]

            css_class = result_type.lower()

            if result.get("keyword"):
                css_class += " keyword"
                label = "KEYWORD"
            else:
                label = result_type

            line_a = result.get("line_a")
            line_b = result.get("line_b")

            text_a = get_line_text(line_a)
            text_b = get_line_text(line_b)

            number_a = get_line_number(line_a)
            number_b = get_line_number(line_b)

            if result_type == "CHANGED":
                html_a, html_b = html_diff(
                    text_a,
                    text_b
                )

                file.write(
                    f'<div class="row {css_class}">'
                    f'<span class="label">[{label}]</span>'
                    f'<span class="file-a">'
                    f'{escape(Path(file_a).name)}'
                    f'</span> '
                    f'<span class="line-number">'
                    f'Line {number_a}'
                    f'</span> '
                    f'{html_a}'
                    f'</div>\n'
                )

                file.write(
                    f'<div class="row {css_class}">'
                    f'<span class="label">[{label}]</span>'
                    f'<span class="file-b">'
                    f'{escape(Path(file_b).name)}'
                    f'</span> '
                    f'<span class="line-number">'
                    f'Line {number_b}'
                    f'</span> '
                    f'{html_b}'
                    f'</div>\n'
                )

            elif result_type in ("SAME", "REMOVED"):
                file.write(
                    f'<div class="row {css_class}">'
                    f'<span class="label">[{label}]</span>'
                    f'<span class="file-a">'
                    f'{escape(Path(file_a).name)}'
                    f'</span> '
                    f'<span class="line-number">'
                    f'Line {number_a}'
                    f'</span> '
                    f'{escape(text_a)}'
                    f'</div>\n'
                )

            elif result_type == "ADDED":
                file.write(
                    f'<div class="row {css_class}">'
                    f'<span class="label">[{label}]</span>'
                    f'<span class="file-b">'
                    f'{escape(Path(file_b).name)}'
                    f'</span> '
                    f'<span class="line-number">'
                    f'Line {number_b}'
                    f'</span> '
                    f'{escape(text_b)}'
                    f'</div>\n'
                )

        file.write(
            '<div class="summary">'
        )

        file.write(
            '<h2>Summary</h2>'
        )

        for name in (
            "TOTAL",
            "SAME",
            "CHANGED",
            "ADDED",
            "REMOVED",
        ):
            file.write(
                f'<div>{name}: '
                f'{statistics.get(name, 0):,}'
                f'</div>'
            )

        file.write(
            '</div>'
        )

        file.write(
            '</body></html>'
        )