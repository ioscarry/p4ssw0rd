def timeToString(seconds):
    if not seconds:
        return "milliseconds"
    if seconds >= 3155692600:
        return "centuries"
    if seconds >= 315569260:
        return "{} decades".format(seconds // 315569260)
    if seconds >= 31556926:
        return "{} years".format(seconds // 31556926)
    if seconds >= 2629743:
        return "{} months".format(seconds // 2629743)
    if seconds >= 604800:
        return "{} weeks".format(seconds // 604800)
    if seconds >= 86400:
        return "{} days".format(seconds // 86400)
    if seconds >= 3600:
        return "{} hours".format(seconds // 3600)
    if seconds >= 60:
        return "{} minutes".format(seconds // 60)
    return "{} seconds".format(seconds)