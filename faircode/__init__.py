"""Fair Code - dataset representation profiler.

The diagnostic counterpart to the project's bias audits: instead of measuring a
model's prediction gap, `faircode` audits a dataset's demographic representation
*before* any model is trained.

    from faircode import profile
    import pandas as pd
    result = profile(pd.read_csv("data.csv"))

See faircode/SPEC.md for the analysis spec shared with the web engine.
"""

from .profiler import profile

__all__ = ["profile"]
__version__ = "0.1.0"
