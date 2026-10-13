def process_data(data):
    if not isinstance(data, list):
        raise TypeError("data must be a list of strings")

    processed = []
    seen = set()

    for index, item in enumerate(data):
        if not isinstance(item, str):
            raise TypeError(
                f"item at index {index} must be a string"
            )

        normalized = " ".join(item.split()).upper()

        if not normalized:
            continue

        if normalized not in seen:
            seen.add(normalized)
            processed.append(normalized)

    return processed
