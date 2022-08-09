from math import sqrt, log


def calculate(ps: float, pd: float, pvw: float) -> int:
    rootVs = sqrt(abs(1060 * pvw) ** 2 - 282642.64 * (ps - pd))
    vs = (1060 * pvw - rootVs) / 1060
    root = sqrt(abs(log(ps/pd) * (vs - pvw)) ** 2 -
                vs * (vs - pvw) * (log(ps / pd) ** 2))

    yyStart = (-1 * log(ps/pd) * (vs - pvw) + root) / vs

    return round(yyStart, 1)
