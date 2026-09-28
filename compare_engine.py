import sys

from config import load_config
from log_reader import read_file
from parser import split_into_node_blocks
from node_aligner import align_node_blocks
from comparator import build_comparisons, calculate_statistics
from filters import load_rules, filter_results
from reporter import write_text_report, write_html_report


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print("python.exe compare_engine.py <file1> <file2>")
        sys.exit(1)

    file_a = sys.argv[1]
    file_b = sys.argv[2]

    config = load_config()

    keywords = load_rules(config["keyword_file"])
    excludes = load_rules(config["exclude_file"])

    print(f"Reading: {file_a}")
    lines_a = read_file(file_a)

    print(f"Reading: {file_b}")
    lines_b = read_file(file_b)

    print(f"Lines A: {len(lines_a):,}")
    print(f"Lines B: {len(lines_b):,}")

    blocks_a = split_into_node_blocks(lines_a, config)
    blocks_b = split_into_node_blocks(lines_b, config)

    print(f"Nodes A: {len(blocks_a):,}")
    print(f"Nodes B: {len(blocks_b):,}")

    aligned_blocks = align_node_blocks(blocks_a, blocks_b)

    results = build_comparisons(
        aligned_blocks,
        file_a,
        file_b,
        config
    )

    results = filter_results(
        results,
        keywords,
        excludes,
        config
    )

    statistics = calculate_statistics(results)

    write_text_report(
        results,
        statistics,
        file_a,
        file_b,
        config
    )

    write_html_report(
        results,
        statistics,
        file_a,
        file_b,
        config
    )

    print()
    print("Comparison completed.")
    print(f"Text report: {config['text_report']}")
    print(f"HTML report: {config['html_report']}")


if __name__ == "__main__":
    main()