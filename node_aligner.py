from difflib import SequenceMatcher


def get_node_keys(blocks):
    return [
        block["node_key"]
        for block in blocks
    ]


def make_pair(block_a=None, block_b=None, status=None):
    return {
        "block_a": block_a,
        "block_b": block_b,
        "status": status,
    }


def align_replace_region(blocks_a, blocks_b):
    aligned = []

    keys_a = get_node_keys(blocks_a)
    keys_b = get_node_keys(blocks_b)

    matcher = SequenceMatcher(
        None,
        keys_a,
        keys_b,
        autojunk=False
    )

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                aligned.append(
                    make_pair(
                        blocks_a[i1 + offset],
                        blocks_b[j1 + offset],
                        "MATCHED"
                    )
                )

        elif tag == "delete":
            for block in blocks_a[i1:i2]:
                aligned.append(
                    make_pair(
                        block_a=block,
                        status="A_ONLY"
                    )
                )

        elif tag == "insert":
            for block in blocks_b[j1:j2]:
                aligned.append(
                    make_pair(
                        block_b=block,
                        status="B_ONLY"
                    )
                )

        elif tag == "replace":
            sub_a = blocks_a[i1:i2]
            sub_b = blocks_b[j1:j2]

            if len(sub_a) == 1 and len(sub_b) == 1:
                aligned.append(
                    make_pair(
                        sub_a[0],
                        sub_b[0],
                        "DIFFERENT_NODE"
                    )
                )
            else:
                aligned.extend(
                    align_replace_region(
                        sub_a,
                        sub_b
                    )
                )

    return aligned


def align_node_blocks(blocks_a, blocks_b):
    return align_replace_region(
        blocks_a,
        blocks_b
    )