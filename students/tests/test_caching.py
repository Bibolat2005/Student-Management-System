import logging
from django.core.cache import cache
from rest_framework.test import APITestCase
from django.core.cache import cache

class CachingTest(APITestCase):
    def test_caching(self):
        expected_data = [{'name': 'Bibolat'}]
        cache.set('students_list_', expected_data, timeout=300)  
        
        cached_data = cache.get('students_list_')
        self.assertEqual(cached_data, expected_data)