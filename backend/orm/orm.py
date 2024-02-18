from typing import List, Literal, TypedDict

Participant = TypedDict(
    "Participant",
    {
        "name": str,
        "age": int,
        "gender": Literal["M", "F"] | None,
        "finish_time": int | None,
        "finished": bool,
        "started": bool,
    },
)

Race = TypedDict(
    "Race",
    {
        "id": int,
        "datasport_id": int,
        "name": str,
        "distance": float,
    },
)


def race_from_row(row) -> Race:
    return {
        "id": row[0],
        "datasport_id": row[1],
        "name": row[2],
        "distance": row[3],
    }


def get_all_races(conn) -> List[Race]:
    races: List[Race] = []

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM races;")
        result = cur.fetchall()
        for row in result:
            races.append(race_from_row(row))

    return races
