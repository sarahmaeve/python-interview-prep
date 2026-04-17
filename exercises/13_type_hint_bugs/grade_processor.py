"""Student grade processing pipeline.

Parses raw student data, calculates GPAs, builds honor rolls,
merges records from multiple sources, and formats transcripts.

Each annotation below documents the INTENDED contract.  The bugs
violate their own annotations — if you ran mypy over this module,
every one of them would be flagged.
"""

from typing import TypedDict


# The raw JSON shape the parser is fed.  Note student_id is `int` in the
# source data, but StudentRecord stores it as `str` (upstream decision).
class RawStudent(TypedDict):
    name: str
    student_id: int
    grades: dict[str, float]


class StudentRecord:
    def __init__(self, name: str, student_id: str,
                 grades: dict[str, float]) -> None:
        self.name: str = name
        self.student_id: str = student_id
        # grades is a dict mapping course name -> grade (e.g. {"Math": 3.7}).
        self.grades: dict[str, float] = grades


def parse_records(raw_data: list[RawStudent]) -> list[StudentRecord]:
    """Convert a list of raw dicts (e.g. from JSON) into StudentRecord objects."""
    records: list[StudentRecord] = []
    for raw in raw_data:
        record = StudentRecord(
            name=raw["name"],
            student_id=raw["student_id"],
            grades=raw.get("grades", {}),
        )
        records.append(record)
    return records


def calculate_gpa(record: StudentRecord) -> float:
    """Return the student's GPA (average of all grades)."""
    if not record.grades:
        return

    total = sum(record.grades.values())
    return total / len(record.grades)


def get_honor_roll(records: list[StudentRecord],
                   min_gpa: float = 3.5) -> list[str]:
    """Return a list of names of students whose GPA meets the threshold."""
    honor: list[str] = []
    for record in records:
        gpa = calculate_gpa(record)
        if gpa >= min_gpa:
            honor.append(record.name)

    if not honor:
        return None

    return honor


def merge_records(existing: StudentRecord, new: StudentRecord) -> StudentRecord:
    """Merge two records for the same student, combining their grades."""
    combined_grades = list(existing.grades.items()) + list(new.grades.items())
    merged = StudentRecord(
        name=existing.name,
        student_id=existing.student_id,
        grades=combined_grades,
    )
    return merged


def format_transcript(record: StudentRecord) -> str:
    """Return a formatted transcript string for the student."""
    lines: list[str] = []
    lines.append(f"Transcript for {record.name} (ID: {record.student_id.upper()})")
    lines.append("-" * 40)
    for course, grade in record.grades.items():
        lines.append(f"  {course}: {grade:.1f}")
    gpa = calculate_gpa(record)
    lines.append("-" * 40)
    lines.append(f"  GPA: {gpa:.1f}")
    return "\n".join(lines)
