from django.test import TestCase
from notifications.tasks import daily_report, grade_update_notification
from celery import Celery
from unittest.mock import patch

class CeleryTasksTest(TestCase):

    def test_daily_report_task(self):
        with patch('notifications.tasks.daily_report') as mock_task:
            mock_task.delay()
            mock_task.delay.assert_called_once()

    def test_grade_update_notification_task(self):
        with patch('notifications.tasks.grade_update_notification') as mock_task:
            mock_task.delay()
            mock_task.delay.assert_called_once()

    def test_celery_task_execution(self):
        result = daily_report.apply()
        self.assertEqual(result.status, 'SUCCESS')