import datetime as dt


def year(request):
    """
    Добавляет переменную с текущим годом.
    """
    now = dt.datetime.now()
    now_year = str(now.year)
    return {'year': now_year}
