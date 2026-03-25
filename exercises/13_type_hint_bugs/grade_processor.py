"""Student grade processing pipeline.

Parses raw student data, calculates GPAs, builds honor rolls,
merges records from multiple sources, and formats transcripts.
"""


class StudentRecord:
    def __init__(self, name, student_id, grades):
        self.name = name
        self.student_id = student_id
        self.grades = grades  # course name -> grade (e.g. {"Math": 3.7})


def parse_records(raw_data):
    """Convert a list of raw dicts (e.g. from JSON) into StudentRecord objects."""
    records = []
    for raw in raw_data:
        record = StudentRecord(
            name=raw["name"],
            student_id=raw["student_id"],  # BUG 2: raw value is int, not str
            grades=raw.get("grades", {}),
        )
        records.append(record)
    return records


def calculate_gpa(record):
    """Return the student's GPA (average of all grades)."""
    if not record.grades:
        return  # BUG 1: returns None instead of a float

    total = sum(record.grades.values())
    return total / len(record.grades)


def get_honor_roll(records, min_gpa=3.5):
    """Return a list of names of students whose GPA meets the threshold."""
    honor = []
    for record in records:
        gpa = calculate_gpa(record)
        if gpa >= min_gpa:
            honor.append(record.name)

    if not honor:
        return None  # BUG 3: returns None instead of empty list

    return honor


def merge_records(existing, new):
    """Merge two records for the same student, combining their grades."""
    combined_grades = list(existing.grades.items()) + list(new.grades.items())
    # BUG 4: assigns a list of tuples instead of converting back to dict
    merged = StudentRecord(
        name=existing.name,
        student_id=existing.student_id,
        grades=combined_grades,
    )
    return merged


def format_transcript(record):
    """Return a formatted transcript string for the student."""
    lines = []
    lines.append(f"Transcript for {record.name} (ID: {record.student_id.upper()})")
    lines.append("-" * 40)
    for course, grade in record.grades.items():
        lines.append(f"  {course}: {grade:.1f}")
    gpa = calculate_gpa(record)
    lines.append("-" * 40)
    lines.append(f"  GPA: {gpa:.1f}")
    return "\n".join(lines)
