import requests

for i in range(1, 101):
    url = "http://192.168.1.100:5000/recommend?user_id=" + str(i)

    start_pos = url.find('user_id=') + len('user_id=')
    user_id = url[start_pos:]
    data = {'user_id': user_id}

    response = requests.post(url, json=data)
    print(response.json())
    print(response.elapsed.total_seconds()) 