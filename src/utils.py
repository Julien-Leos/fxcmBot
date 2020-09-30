def dateDiffInMillisecond(date1, date2):
    delta = date1 - date2
    return (delta.days * 24 * 60 * 60 * 1000) + (delta.seconds * 1000) + (delta.microseconds / 1000)
