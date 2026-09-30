PARIS_ARRONDISSEMENT_CODES = range(75101, 75121)


def commune_label(commune_code: str) -> str:
    """Human-readable name of a commune: "Paris 1er", "Paris 11e"... or the code itself."""
    if commune_code.isdigit() and int(commune_code) in PARIS_ARRONDISSEMENT_CODES:
        arrondissement = int(commune_code) - 75100
        return f"Paris {arrondissement}{'er' if arrondissement == 1 else 'e'}"
    return commune_code
