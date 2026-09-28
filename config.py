from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent

CONFIG_DIR = SCRIPT_DIR / "config"
REPORTS_DIR = SCRIPT_DIR / "reports"


def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    return {
        "ignore_first_columns": 5,
        "remove_timestamps": True,
        "show_same": False,

        "keyword_file": CONFIG_DIR / "keywords.txt",
        "exclude_file": CONFIG_DIR / "exclude.txt",

        "text_report": REPORTS_DIR / "compare_results.txt",
        "html_report": REPORTS_DIR / "compare_results.html",

        "rules_ignore_case": True,

        "compress_repeats": True,
        "min_repeat_count": 3,

        "change_threshold": 0.55,
        "change_window": 30,
        "min_length_ratio": 0.60,

        "mark_changed_differences": True,
        "difference_marker": "^",

        "progress_bar_width": 30,
        "progress_update_seconds": 0.15,

        "add_test_to_flow_node": True,
        "flow_node_text": "Start flow node",
    }