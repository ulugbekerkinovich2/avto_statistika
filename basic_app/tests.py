from django.test import TestCase
from collections import Counter
# Create your tests here.
fruits = ['app', 'bann', 'ban', 'banana', 'app', 'asdasd', 'app']
fruits_count = Counter(fruits)
print(fruits_count)
