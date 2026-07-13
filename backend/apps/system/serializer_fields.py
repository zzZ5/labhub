def file_field_size(file_field):
    if not file_field:
        return 0
    try:
        return file_field.size
    except (OSError, ValueError):
        return 0
