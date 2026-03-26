def create_pipeline(*transforms):
    """Return a function that applies each transform in order to a single record.

    If any transform returns None, the record is filtered out (the pipeline
    returns None for that record).

    Args:
        *transforms: Zero or more callables. With no transforms, the pipeline
                     returns the record unchanged. Each callable takes a dict
                     and returns a dict or None.

    Returns:
        A callable that takes a dict and returns a dict or None.
    """
    pass


def run_pipeline(pipeline, records):
    """Apply *pipeline* to each record, returning only non-None results.

    Args:
        pipeline: A callable (from create_pipeline) that processes one record.
        records: An iterable of dicts.

    Returns:
        A list of transformed dicts (filtered records are excluded).
    """
    pass


def make_field_mapper(field, func):
    """Return a transform that applies *func* to record[field].

    The original record is not mutated — return a new dict.
    If the field is missing from the record, return the record unchanged.

    Args:
        field: The key to transform.
        func: A callable to apply to the field's value.

    Returns:
        A transform callable.
    """
    pass


def make_filter(predicate):
    """Return a transform that keeps records where predicate(record) is True.

    Returns None for records that don't match (filtering them out).

    Args:
        predicate: A callable that takes a dict and returns bool.

    Returns:
        A transform callable.
    """
    pass


def make_default(field, default_value):
    """Return a transform that adds *field* with *default_value* if missing.

    If the field already exists, the record is returned unchanged.

    Args:
        field: The key to set.
        default_value: The value to use if the key is missing.

    Returns:
        A transform callable.
    """
    pass
