from requests import get, post, delete, put

print(get('http://localhost:8080/api/publications/').json())
