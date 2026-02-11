import requests 


GOOGLE_URL = "http://www.google.com"
BOODE_URL = "http://boodelyboo.com"

CHOSEN_URL = GOOGLE_URL

res = requests.get(CHOSEN_URL)
print(res.status_code)
print(res.headers)
print(res.text[:500])  # Print the first 500 characters of the response body


if __name__ == "__main__":
    pass