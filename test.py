import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Replace with your actual API key
API_KEY = os.getenv("CLANWARE_API_KEY")

# Base URL for the Clanware Justice API
BASE_URL = 'https://api.clanware.org/api/v1'

# Headers including the API key for authentication
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'Accept': 'application/json'
}

def check_user_status(user_id):
    """
    Checks if a user is listed as an exploiter or degenerate.
    
    Parameters:
        user_id (str): The Roblox user ID to check.
        
    Returns:
        dict: A dictionary containing the user's status.
    """
    try:
        response = requests.get(f'{BASE_URL}/users/{user_id}', headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        return {
            'user_id': user_id,
            'is_exploiter': data.get('is_exploiter', False),
            'is_degenerate': data.get('is_degenerate', False),
            'details': data.get('details', {})
        }
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'An error occurred: {err}')
    return None

# Example usage
if __name__ == '__main__':
    user_id = input('Enter the Roblox user ID to check: ')
    status = check_user_status(user_id)
    if status:
        print(f"User ID: {status['user_id']}")
        print(f"Is Exploiter: {status['is_exploiter']}")
        print(f"Is Degenerate: {status['is_degenerate']}")
        if status['details']:
            print("Details:")
            for key, value in status['details'].items():
                print(f"  {key}: {value}")
    else:
        print('Failed to retrieve user status.')
