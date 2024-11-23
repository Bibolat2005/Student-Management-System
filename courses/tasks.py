from celery import shared_task

@shared_task
def send_course_update_notifications():
    return True
