"""Telecom Tower Maintenance Tracker.

A maintenance tracker module for telecom towers that logs towers and faults,
records servicing, lists overdue inspection sites, and rates tower risks.
"""

import sqlite3

# Module-level store for connection and operational metrics
STATE = {
    "conn": None,
    "service_count": 0,
}


def get_connection(db_path=":memory:"):
    """Create and initialize the SQLite database connection with schema.

    Args:
        db_path: Path to database or memory specifier (default: ':memory:').

    Returns:
        sqlite3.Connection: Active database connection.
    """
    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS towers (
            id INTEGER PRIMARY KEY,
            site TEXT NOT NULL,
            last_service INTEGER NOT NULL,
            faults INTEGER NOT NULL
        )
        """
    )
    connection.commit()
    return connection


def init_state(db_path=":memory:"):
    """Initialize or reset the module-level tracker state."""
    STATE["conn"] = get_connection(db_path)
    STATE["service_count"] = 0


def add_tower(site, last_service, faults=0):
    """Add a new tower record to the database using parameterized queries.

    Args:
        site: Name or identifier of the telecom tower site.
        last_service: Year when the tower was last serviced.
        faults: Number of recorded faults (default: 0).
    """
    if STATE["conn"] is None:
        init_state()

    STATE["conn"].execute(
        "INSERT INTO towers (site, last_service, faults) VALUES (?, ?, ?)",
        (site, last_service, faults),
    )
    STATE["conn"].commit()


def service_tower(tower_id, year):
    """Record maintenance servicing for a specific tower and reset faults.

    Args:
        tower_id: Primary key ID of the tower.
        year: Year the service was performed.

    Returns:
        bool: True if service was successful, False otherwise.
    """
    if STATE["conn"] is None:
        init_state()

    try:
        STATE["conn"].execute(
            "UPDATE towers SET last_service = ?, faults = 0 WHERE id = ?",
            (year, tower_id),
        )
        STATE["conn"].commit()
        STATE["service_count"] += 1
        return True
    except sqlite3.Error as err:
        print(f"Service failed for tower {tower_id}: {err}")
        return False


def overdue(year):
    """Find all tower sites overdue for maintenance by 2 or more years.

    Args:
        year: The current reference year to check against.

    Returns:
        list[str]: Names of overdue tower sites.
    """
    if STATE["conn"] is None:
        init_state()

    rows = STATE["conn"].execute(
        "SELECT site, last_service FROM towers"
    ).fetchall()
    return [site for site, last in rows if year - last >= 2]


def risk_level(tower_id):
    """Determine the risk level of a tower based on fault count.

    Args:
        tower_id: Primary key ID of the tower.

    Returns:
        str: 'high' if faults exceed 3, otherwise 'normal'.
    """
    if STATE["conn"] is None:
        init_state()

    row = STATE["conn"].execute(
        "SELECT faults FROM towers WHERE id = ?",
        (tower_id,),
    ).fetchone()
    if row and row[0] > 3:
        return "high"
    return "normal"


def snapshot():
    """Retrieve an in-memory snapshot list of all tower records.

    Returns:
        list[tuple]: List of all tower records currently in the database.
    """
    if STATE["conn"] is None:
        init_state()

    return STATE["conn"].execute("SELECT * FROM towers").fetchall()


def main():
    """Execute demonstration scenario for telecom tower maintenance tracker."""
    init_state()

    add_tower("Ridge-A", 2021, 5)
    add_tower("Coast-B", 2024)
    service_tower(2, 2025)

    total = len(snapshot())
    print(overdue(2025), risk_level(1), total, STATE["service_count"])

    if STATE["conn"]:
        STATE["conn"].close()


if __name__ == "__main__":
    main()
