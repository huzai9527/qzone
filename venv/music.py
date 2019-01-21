import requests
url = 'http://music.163.com/api/v1/resource/comments/R_SO_4_32785700?limit=100&offset=1'
raw = requests.get(url=url).text
print()