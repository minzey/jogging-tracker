from .models import JogRecord

def weekly_distance_and_speed_average(jogger, week_start_date, week_end_date):
    """
    Computes weekly average for a given jogger and week.
    """
    jog_objs = JogRecord.objects.filter(jogger=jogger, date__range=[week_start_date, week_end_date])
    total_distance = 0
    total_time = 0
    for jog_obj in jog_objs:
        total_distance += jog_obj.distance
        total_time += jog_obj.time

    try:
        total_speed = total_distance / total_time
    except ZeroDivisionError as zde:
        total_speed = 0

    data = {
        "jogger_id": jogger.id,
        "week_start_date": week_start_date.strftime("%Y-%m-%d"),
        "week_end_date": week_end_date.strftime("%Y-%m-%d"),
        "average_distance": round(total_distance / 7, 2),
        "average_speed": round(total_speed / 7, 2)
    }

    return data




