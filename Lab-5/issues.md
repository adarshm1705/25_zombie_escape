# Static Code Analysis Issues Report

**Target File:** `tower_maintenance.py`  
**Tools Used:** Pylint, Bandit, Flake8  

---

## Documented Issues Table

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---|---|---|
| **SQL Injection Vulnerability** | Security (Bandit B608) | 11 | In `addTower`, the SQL `INSERT` statement was assembled using Python string interpolation (`'%s', %d, %d` % (site, last_service, faults)). This exposes the database to SQL injection attacks if input values contain unescaped SQL syntax. | Replaced string interpolation with parameterized queries using `?` placeholders: `VALUES (?, ?, ?)` and passed the arguments as a safe parameter tuple `(site, last_service, faults)`. |
| **Insecure Deserialization via Pickle** | Security (Bandit B301, B403) | 1, 43 | The `snapshot()` function serialized and deserialized query results using `pickle.loads(pickle.dumps(...))`. Deserializing untrusted pickle streams can lead to arbitrary code execution. Furthermore, using pickle solely to duplicate rows returned by `fetchall()` is dangerous and redundant. | Removed `import pickle` entirely and returned the row tuples directly from `conn.execute("SELECT * FROM towers").fetchall()`. |
| **Overly Broad Exception Handling** | Quality / Reliability (Pylint W0718) | 20 | In `serviceTower`, a generic `except Exception:` block caught all exceptions, masking unforeseen runtime errors (e.g., database connection drops, schema errors, or system signals) and printing a non-informative error message. | Restricted the exception handler to `sqlite3.Error as err` and logged contextual diagnostic details: `f"Service failed for tower {tower_id}: {err}"`. |
| **Hardcoded Secret / Password String** | Security (Bandit B105) | 6 | A sensitive password `NOC_PASSWORD = "tower-noc-77"` was hardcoded at module level. Hardcoded credentials risk exposure in version control and repositories. The variable was also unused dead code. | Removed the unused hardcoded password. In production systems, credentials should be retrieved from environment variables or a secret vault. |
| **Global State Mutation via `global` Statement** | Quality / Maintainability (Pylint W0603) | 7, 16, 19 | The variable `service_count` was modified across function calls using the `global` statement. Using global mutable state causes tight coupling, impedes unit testing, and is unsafe in multi-threaded environments. | Encapsulated mutable database connection and service count within a structured state dictionary (`STATE`), eliminating the `global` statement while maintaining explicit initialization. |
| **Non-Compliant Function Naming (PEP 8)** | Style (Pylint C0103) | 10, 15, 34 | Function names `addTower`, `serviceTower`, and `riskLevel` violated the Python PEP 8 naming convention, which mandates `snake_case` for function identifiers. | Renamed functions to standard snake_case: `add_tower`, `service_tower`, and `risk_level`. |
| **Missing Module and Function Docstrings** | Quality (Pylint C0114, C0116) | 1, 10, 15, 25, 34, 42, 46 | The module and its functions completely lacked docstrings, violating PEP 257 documentation conventions and reducing code maintainability. | Added comprehensive docstrings to the module and every function explaining their purpose, arguments, and return types. |
| **PEP 8 Formatting, Line Length & Spacing** | Style (Flake8 E501, E303, E225; Pylint C0301, R1705) | 5, 11, 18, 25, 35, 36-39, 50 | Lines exceeded the 79/100 character limit; too many consecutive blank lines were present; missing whitespace around operator (`total=len(...)`); and unnecessary `else` after `return` in `riskLevel`. | Refactored long SQL strings to multi-line statements, normalized blank lines to standard spacing, added operator whitespace, simplified returns, and guarded execution with `if __name__ == "__main__":`. |

---

## Summary of Fixes & Score Improvements

* **Initial Pylint Score:** 5.14 / 10
* **Final Pylint Score:** **10.00 / 10**
* **Initial Bandit Issues:** 4 issues (2 Medium, 2 Low)
* **Final Bandit Issues:** **0 issues**
* **Initial Flake8 Errors:** 7 errors (E501, E303, E225)
* **Final Flake8 Errors:** **0 errors**
* **Functional Integrity:** Verified with identical output `['Ridge-A'] high 2 1`.

