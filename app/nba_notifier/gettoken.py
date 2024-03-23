import requests
from bs4 import BeautifulSoup  # You might need to install BeautifulSoup

# Initialize a session object to persist cookies
session = requests.Session()


def get_csrf_token(url):
    # Fetch the form page
    response = session.get(url)
    if response.status_code == 200:
        # Use BeautifulSoup to parse the HTML and extract the CSRF token value
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find(
            "input", dict(
                name="csrfmiddlewaretoken")).get("value")
        return csrf_token
    else:
        print(
            f"Failed to fetch the form page. Status code: {response.status_code}")
        return None


# URL of the Django form page
form_url = "http://127.0.0.1:8000/game-monitor/phone-form/"

# Get CSRF token
csrf_token = get_csrf_token(form_url)

# Check if CSRF token was successfully retrieved
if csrf_token:
    print(f"CSRF Token: {csrf_token}")
    # Prepare headers
    headers = {
        "Referer": form_url,
        "Content-Type": "application/x-www-form-urlencoded"}
    # Data payload including the CSRF token
    data = {"csrfmiddlewaretoken": csrf_token, "phone_number": "5105194907"}
    # Submit the form
    response = session.post(form_url, headers=headers, data=data)
    if response.status_code == 200:
        print("Form submitted successfully.")
    else:
        print(f"Form submission failed. Status code: {response.status_code}")
else:
    print("Could not retrieve CSRF token.")
