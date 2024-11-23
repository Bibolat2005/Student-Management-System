# from rest_framework.test import APITestCase
# from rest_framework import status
# from users.models import CustomUser
# from analytics.models import ThrottlingMetrics

# class ThrottlingStatsTests(APITestCase):
#     def setUp(self):
#         self.admin_user = CustomUser.objects.create_superuser(
#             email="admin@example.com", password="admin123", username="admin"
#         )
#         self.normal_user = CustomUser.objects.create_user(
#             email="user@example.com", password="user123", username="user"
#         )
#         ThrottlingMetrics.objects.create(user=self.normal_user, daily_request_count=5)

#         self.admin_token = self.client.post(
#             "/api/users/auth/jwt/create/",
#             {"email": "admin@example.com", "password": "admin123"}
#         ).data["access"]

#     def test_admin_can_view_stats(self):
#         self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.admin_token}")
#         response = self.client.get("/api/analytics/stats/")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('user__username', response.data[0])
#         self.assertIn('daily_request_count', response.data[0])
#         self.assertIn('last_request_time', response.data[0])