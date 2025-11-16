def extract_expirations(strikes_data):
    expirations = set()

    for row in strikes_data:
        if "expirDate" in row:
            expirations.add(row["expirDate"])

    return sorted(list(expirations))
