"""
Minimal decoder for CSO PxStat's JSON-stat 2.0 dataset responses.

JSON-stat 2.0 packs an N-dimensional cube into a flat `value` array. The
`id` list gives the dimension order and `size` gives each dimension's
cardinality in that same order; the flat array is indexed in row-major
order with the *last* dimension varying fastest (standard JSON-stat 2.0
convention). Each dimension's `category.index` maps a positional index to
a category code, and `category.label` maps that code to a human label.

This module has no CSO-specific knowledge - it just decodes the cube into
an iterable of (dict of dimension_code -> category_code, value) tuples,
which callers can then interpret using the dimension's `category.label`
lookups to get human-readable labels.
"""

from typing import Any, Iterator


def iter_jsonstat_cells(dataset: dict) -> Iterator[tuple[dict, Any]]:
    """
    Yield (dim_codes, value) for every cell in a JSON-stat 2.0 dataset,
    where dim_codes is a dict mapping each dimension id to the category
    code active for that cell.
    """
    dim_ids: list[str] = dataset["id"]
    sizes: list[int] = dataset["size"]
    values: list = dataset["value"]
    dimension = dataset["dimension"]

    # Pre-fetch each dimension's ordered list of category codes.
    dim_indexes = [dimension[d]["category"]["index"] for d in dim_ids]

    total = 1
    for s in sizes:
        total *= s
    if total != len(values):
        raise ValueError(
            f"JSON-stat size mismatch: product(size)={total} != len(value)={len(values)}"
        )

    # Precompute strides for row-major decoding (last dimension fastest).
    strides = [1] * len(sizes)
    for i in range(len(sizes) - 2, -1, -1):
        strides[i] = strides[i + 1] * sizes[i + 1]

    for flat_idx, value in enumerate(values):
        if value is None:
            continue
        remainder = flat_idx
        dim_codes = {}
        for dim_id, size, stride, index_list in zip(dim_ids, sizes, strides, dim_indexes):
            pos = remainder // stride
            remainder = remainder % stride
            dim_codes[dim_id] = index_list[pos]
        yield dim_codes, value


def label_for(dataset: dict, dim_id: str, code: str) -> str:
    """Return the human-readable label for a category code in a dimension."""
    labels = dataset["dimension"][dim_id]["category"].get("label", {})
    return labels.get(code, code)
