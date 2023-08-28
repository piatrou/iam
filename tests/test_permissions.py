import unittest
import requests

API_URI = 'http://127.0.0.1:5000'


def get_token():
    url = f"{API_URI}/api/iam/token"
    payload = {
        "username": "admin",
        "password": "admin"
    }
    headers = {"Content-Type": "application/json"}

    response = requests.request("POST", url, json=payload, headers=headers)
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


class PermissionTest(unittest.TestCase):

    def test_create(self):
        payload = {
            "name": "test_can_edit",
            "description": "Test descriptions"
        }
        response = requests.post(f'{API_URI}/api/iam/permission', headers=get_token(), json=payload)
        self.assertEqual(response.status_code, 201, f'Permission was not created {response.status_code}')


if __name__ == '__main__':
    unittest.main()
