import discord
from discord.ext import commands
from discord import app_commands
import json
import requests
import time
from datetime import datetime
from requests.exceptions import ConnectionError, HTTPError
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
import math
import matplotlib
matplotlib.use('Agg') # Set non-interactive backend for Matplotlib BEFORE importing pyplot
import matplotlib.pyplot as plt
import io
from PIL import Image
import asyncio # Import asyncio
from flask import Flask
import threading

load_dotenv()

# Discord token (still recommended to keep token in .env or environment variable)
TOKEN = os.getenv("TOKEN")
XTRACKER_API_KEY = os.getenv("XTRACKER_API_KEY")
CLANWARE_API_KEY = os.getenv("CLANWARE_API_KEY")
CLANWARE_BASE_URL = "https://justice.clanware.org/api/justice/legacy" # Define the Clanware base URL

# New Spreadsheet ID from your provided Google Sheets link
SPREADSHEET_ID = "1C-Jd9G7XQVDhiKfJC0PyFMPr5tqXURrKY5KH9Q_1F6s"

# Your Google Service Account JSON credentials as a dict (paste your JSON here)
SERVICE_ACCOUNT_INFO = {
  "type": "service_account",
  "project_id": "searchy-428415",
  "private_key_id": "a672afb4b7fd10faf5237fc3422f33e179a4d9cb",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDrOdNHpyDbWb16\nYfWe3U+tc32yL05Z7QCNHJxJVG0xEhprkuaJOu4u1vKyDNqRkA+wy2yM+d6dgmkv\nsJgDa7yYDAa5DMp2SVYxSNF/n5ky+OWWu2raR8XlL1WbJ94CRALsPKlSr+7jGPJd\n32xpACS6DvbtHX3CHHFlU9/1dF2UMnL6uCyYFd2BAWn+HIlr0HlbMlhxt8MkhURx\ngObAk73DVVzPBMlWs+vtqPjRhmVVU/t/32V9OghJwYkKUUM/8JwLrYdpNgvCj/y8\nqEZlqR1IN6JpTt4dEFKHOqNDkDW0ZZt7vST6pDkZEVNc84Kl1jpZcb7pAl+kfbyB\nktn6IXa9AgMBAAECggEACwTUbuDXWy8i/x6joOOBHgDw/G3W38OIaRPUBmNcEhZl\nAnEJN5h5G9yZ1dlgS71R3thIp3n1Aa/gOYmuNUrQtNarYfPFcDETRo/AsJfLV2Xt\na1gwMzV1gbzr567AaZ7B/EsDK4puSFkc0WTr8Sc+kTCuRIFDKNqoPTTmotrmn1B+\nsHB4duA0xkVUUpTxIM9QAiMpmRXyT8fGw1pa30+qMmVQNvcizLFR9gUeEwTaxg1u\n8Hd1nMfj8N9DsxsAQ5tOgvrZgKxlRlFCs5/pnUBFuy01r3bLe9Unlu2mnShCeAwn\np2kVKCy2uhSmchmF+zQkLNL1w51Apg6KzA9lTvYkwQKBgQD39GMJy/hikmAjWnQs\nsNeCS1wujq/y0hI9zin8HWHT148CcNZl4m8m2ra+wDAwNhBHLUD8Gz1qWDxnYuQq\nLswo9Z4+EzA2ABsd/rQZ3/Ci85YSCbRX52NbK5kNaKPSHSrhlcclNQ+Lk9L5ZLr4\nEzr0cIE8bS/ZkuWVx0vKQDeZyQKBgQDy27VKNfYmgQzL5m3ZKld1W0nCzI3I1wc+\naeAnXxsbSArYwqJRH4ltPQznK0a29uM5wFLbGntOU/vT5+jl0Pg+hy/EdLfJ2+2y\neQY/xXAuqRuSUY3v5JHUfrejS+yWQ8otgoBgECPc0YME2gmBAYB5XOufycnUWAp8\n5nT6LrOvVQKBgFAn3sRR/c/Pxehn21p/KIvkVL5wPgzfQCpetU/dJ7zV2FNPqt9w\n3cHPvnfXpTxQnd6EkJdvLuFr+MrrOxsv2av8CtXCWjl6u0ltB0e+Dwp+eCsInBY2\npPXaGDYvd5X6+9vFEYXDq2zRssgQeiir/sj6fazNF0Tcqf9LWALf05mRAoGABamJ\nuIk5i/xGSBq/ROjv0RSny5rpU11wFcxyJXjaMPClEBi5oBqUIa/itSEVLP7knVwW\nknUzmsfqfy5RB8qvfwW332S5REOUbyzTMHlx/CSFOAweuxEhNUsfDPegNICwHg+E\n3riBnYxk+Z/7yL44OJwqAje6NPE4jWDyKUMdfWECgYEA4w5XnCh1hxx/yDz4BBgX\nNh3tvdAlHx2WSbLR0ykAkykFt/hiVpsBqlUdoeQgKcy6I2ztFLSmJUFCcYjR6xZP\n33nn5MRd0HowOVJnUn45hi+Q7uBVPC/vmgKLt8fV9lKG149ZTrKZJRbKVYGtUEFW\nPrpQ9x0kzM5mfAU2iP0RQQs=\n-----END PRIVATE KEY-----\n",
  "client_email": "acceptancecheck@searchy-428415.iam.gserviceaccount.com",
  "client_id": "102839480730277219815",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/acceptancecheck%40searchy-428415.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# Roblox API base URLs
ROBLOX_USERS_API = "https://users.roblox.com/v1"
ROBLOX_FRIENDS_API = "https://friends.roblox.com/v1"
ROBLOX_BADGES_API = "https://badges.roblox.com/v1"
ROBLOX_BADGES_PROXY_API = "https://badges.roproxy.com/v1" # Using roproxy for badge data
ROBLOX_INVENTORY_API = "https://inventory.roblox.com/v2"
ROBLOX_GROUPS_API = "https://groups.roblox.com/v2"

# Setup Discord bot
AWARDED_DATES_BATCH_SIZE = 100 # How many badge IDs to query for awarded dates at once
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree
BLACKLIST_REFRESH_LOCK = threading.Lock()

# Global cache for blacklist
CACHED_BLACKLIST = set()
LAST_BLACKLIST_REFRESH_TIME = 0
BLACKLIST_CACHE_DURATION_SECONDS = 60 * 15  # Cache for 15 minutes

# Setup Google Sheets client
def get_blacklisted_ids():
    global CACHED_BLACKLIST, LAST_BLACKLIST_REFRESH_TIME
    current_time = time.time()

    needs_refresh = not CACHED_BLACKLIST or \
                    (current_time - LAST_BLACKLIST_REFRESH_TIME > BLACKLIST_CACHE_DURATION_SECONDS)

    if needs_refresh:
        if BLACKLIST_REFRESH_LOCK.acquire(blocking=False):
            try:
                # Re-check condition inside lock in case another thread refreshed it
                current_time_in_lock = time.time() # Get fresh time
                if not CACHED_BLACKLIST or \
                   (current_time_in_lock - LAST_BLACKLIST_REFRESH_TIME > BLACKLIST_CACHE_DURATION_SECONDS):
                    print("Refreshing blacklist cache (lock acquired)...")
                    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
                    creds = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
                    client = gspread.authorize(creds)
                    sheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(1)  # second sheet (index 1)
                    blacklist_column = sheet.col_values(4)  # Column D
                    CACHED_BLACKLIST = set(filter(str.isdigit, blacklist_column))  # Only numeric IDs
                    LAST_BLACKLIST_REFRESH_TIME = current_time_in_lock
                    print(f"Blacklist cache refreshed. {len(CACHED_BLACKLIST)} IDs loaded.")
                else:
                    print("Blacklist cache was already refreshed by another thread while acquiring lock.")
            except gspread.exceptions.APIError as e:
                print(f"APIError refreshing blacklist cache: {e}. Using stale cache if available.")
            except Exception as e:
                print(f"Unexpected error refreshing blacklist cache: {e}. Using stale cache if available.")
            finally:
                BLACKLIST_REFRESH_LOCK.release()
        else:
            print("Blacklist refresh already in progress. Using current (potentially stale) cache.")
    else:
        print("Using cached blacklist.")
    return CACHED_BLACKLIST
    

def safe_get(url, method="GET", params=None, json_payload=None, max_retries=3, backoff_factor=1, headers=None):
    for attempt in range(max_retries):
        try:
            print(f"safe_get: Attempt {attempt + 1} for {method} {url} with params {params} and JSON payload {json_payload}")
            if method.upper() == "POST":
                resp = requests.post(url, params=params, json=json_payload, headers=headers, timeout=10)
            elif method.upper() == "GET":
                resp = requests.get(url, params=params, headers=headers, timeout=10)
            else:
                print(f"safe_get: Unsupported method '{method}' for {url}.")
                return None
            resp.raise_for_status()
            return resp
        except requests.exceptions.Timeout:
            print(f"safe_get: Attempt {attempt + 1} timed out for {url}.")
            if attempt == max_retries - 1:
                return None
            time.sleep(backoff_factor * (2 ** attempt))
        except (ConnectionError, HTTPError) as e:
            error_detail = str(e)
            if isinstance(e, HTTPError) and e.response is not None:
                error_detail = f"{e} - Status: {e.response.status_code}, Response: {e.response.text[:200]}"
            print(f"safe_get: Attempt {attempt + 1} failed for {url}. Error: {error_detail}")
            if attempt == max_retries - 1:
                return None
            time.sleep(backoff_factor * (2 ** attempt))
    return None # Fallback if max_retries is 0 or less

def parse_roblox_date(date_str):
    # Robust date parsing based on reference script, handles varying millisecond precision
    # and ensures the format is standardized to what strptime expects with %f.
    original_date_str = date_str # Keep original for logging on error
    try:
        if '.' in date_str:
            parts = date_str.split('.', 1)
            base = parts[0]
            milli_and_z = parts[1]
            
            milliseconds = milli_and_z[:-1] # Remove Z
            if len(milliseconds) > 6: # strptime %f expects up to 6 digits for microseconds
                milliseconds = milliseconds[:6]
            elif len(milliseconds) < 6:
                milliseconds = milliseconds.ljust(6, '0')
            date_str = f"{base}.{milliseconds}Z"
        else:
            # No decimal part, add .000000Z for microseconds
            date_str = date_str[:-1] + ".000000Z"
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError as e:
        print(f"Error parsing date string '{original_date_str}' (processed as '{date_str}'): {e}")
        raise # Re-raise to be handled by the caller

def resolve_roblox_identifier(identifier: str) -> tuple[int | None, str | None]:
    """
    Resolves a Roblox identifier (username or ID) to a User ID.
    Returns: (user_id, error_message). If successful, user_id is int, error_message is None.
             Otherwise, user_id is None, error_message is a string.
    """
    if identifier.isdigit():
        return int(identifier), None
    else:
        # Try to resolve username to ID
        url = f"{ROBLOX_USERS_API}/usernames/users"
        json_payload = {"usernames": [identifier], "excludeBannedUsers": False}
        
        response = safe_get(url, method="POST", json_payload=json_payload)
        if response:
            data = response.json()
            if data.get("data") and len(data["data"]) > 0 and "id" in data["data"][0]:
                return data["data"][0]["id"], None
            else:
                return None, f"Username '{identifier}' not found or API returned unexpected data."
        else:
            return None, f"Error resolving username '{identifier}' using safe_get."

def get_user_info(user_id):
    url = f"{ROBLOX_USERS_API}/users/{user_id}"
    resp = safe_get(url)
    print("info gotten")
    return resp.json() if resp else None

def get_friends_count(user_id):
    url = f"{ROBLOX_FRIENDS_API}/users/{user_id}/friends/count"
    resp = safe_get(url)
    print("Friends Gotten")
    return resp.json().get("count", 0) if resp else 0

def plot_badge_history(date_list, username):
    if not date_list:
        return None
    # Sort and count cumulative badges
    date_list.sort()
    dates = []
    counts = []
    count = 0
    last_date = None
    for d in date_list:
        if last_date != d:
            dates.append(d)
            counts.append(count + 1)    
            last_date = d
        else:
            counts[-1] += 1
        count += 1
    plt.figure(figsize=(10, 5))
    plt.plot(dates, counts, marker='o')
    plt.title(f"{username}'s Roblox Badge History")
    plt.xlabel("Date")
    plt.ylabel("Total Badges")
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return buf

def check_clanware_report(user_id: int, max_retries=3, backoff_factor=1):
    """
    Checks if a Roblox user is flagged by Clanware.
    Returns (success: bool, flagged: bool or error message str)
    """
    if not CLANWARE_API_KEY:
        return False, "Clanware API key not configured."
    print(f"Clanware: Checking user ID: {user_id}")

    url = f"{CLANWARE_BASE_URL}/{user_id}"
    headers = {
        "Authorization": f"Bearer {CLANWARE_API_KEY}",
        "Accept": "application/json",
        "User-Agent": "acceptance/1.0"
    }
    print(f"Clanware: Requesting URL: {url}")

    for attempt in range(max_retries):
        try:
            print(f"Clanware: Attempt {attempt + 1}")
            resp = requests.get(url, headers=headers, timeout=10)
            print(f"Clanware: Response Status Code: {resp.status_code}")
            if resp.status_code == 404:
                print(f"Clanware: User {user_id} not found (404), considered not flagged.")
                return True, False
            if resp.status_code == 403:
                print(f"Clanware: API Forbidden (403) for user {user_id}. Check API key/permissions.")
                return False, "Clanware API HTTP 403 Forbidden: Check your API key and permissions."
            resp.raise_for_status()
            data = resp.json()
            print(f"Clanware: API Response Data for {user_id}: {data}")
            is_flagged = data.get("is_exploiter", False) or data.get("is_degenerate", False)
            print(f"Clanware: User {user_id} is_flagged: {is_flagged}")
            return True, is_flagged
        except requests.exceptions.RequestException as e:
            print(f"Clanware: RequestException on attempt {attempt + 1} for user {user_id}: {e}")
            if attempt == max_retries - 1:
                return False, f"Clanware API request error ({type(e).__name__}): {e}"
            time.sleep(backoff_factor * (2 ** attempt))
    print(f"Clanware: Check failed after all retries for user {user_id}.")
    return False, "Clanware check failed after all retries."

def get_group_roles_data(user_id: int):
    """
    Fetches all group and role information for a user from Roblox API.
    Returns a tuple: (list_of_group_roles | None, is_data_complete: bool).
    'is_data_complete' is False if an error occurred that might result in partial data.
    Returns (None, False) if the initial API call fails.
    """
    all_group_roles = []
    cursor = None
    limit = 100 # Roblox API default limit for this endpoint is often 10, max is 100
    is_complete = True # Assume complete until an error occurs post-initial fetch

    while True:
        url = f"{ROBLOX_GROUPS_API}/users/{user_id}/groups/roles?limit={limit}&sortOrder=Asc"
        if cursor:
            url += f"&cursor={cursor}"

        resp = safe_get(url)
        if not resp:
            # If the first call fails, return None. If a subsequent call fails, return what's been collected.
            # If a subsequent call fails, return what's been collected but mark as incomplete.
            return (None, False) if not all_group_roles else (all_group_roles, False)

        try:
            data = resp.json()
            current_page_data = data.get("data", [])
            all_group_roles.extend(current_page_data)

            cursor = data.get("nextPageCursor")
            if not cursor: # No more pages
                break
        except requests.exceptions.JSONDecodeError:
            print(f"JSONDecodeError fetching group roles for {user_id} from {url}: {resp.text[:200]}")
            # Similar to above: if first call, (None, False), else (partial_data, False)
            is_complete = False # Mark as incomplete
            return (None, False) if not all_group_roles else (all_group_roles, False)
    return all_group_roles, is_complete

def get_all_rank_values_for_group(group_id: int) -> list[int] | None:
    """Fetches all unique rank values for a specific group."""
    all_ranks = set() # Use a set to store unique rank values
    cursor = None
    limit = 100 
    
    print(f"Fetching all roles for group ID: {group_id} to determine rank structure.")
    while True:
        # Using v2 endpoint which is paginated
        url = f"{ROBLOX_GROUPS_API}/groups/{group_id}/roles?limit={limit}&sortOrder=Asc"
        if cursor:
            url += f"&cursor={cursor}"
        
        resp = safe_get(url)
        if not resp:
            print(f"Failed to fetch roles for group {group_id}. Returning None for rank structure.")
            return None # Critical failure to get any role data for this group
        
        try:
            data = resp.json()
            roles_data = data.get("data", [])
            for role in roles_data:
                if 'rank' in role:
                    all_ranks.add(role['rank']) # Add rank to set
            
            cursor = data.get("nextPageCursor")
            if not cursor: # No more pages
                break
        except requests.exceptions.JSONDecodeError:
            print(f"JSONDecodeError fetching roles for group {group_id} from {url}: {resp.text[:200]}")
            return None # Critical failure
            
    if not all_ranks: # Should not happen if group exists and has roles, but good to check
        print(f"No ranks found for group {group_id} after fetching roles.")
        return [] # Return empty list if no ranks were found (e.g., group with no roles?)
        
    return sorted(list(all_ranks)) # Return a sorted list of unique rank values

def get_formatted_group_details(
    group_roles_list: list[dict] | None,
    is_data_complete: bool
) -> tuple[str, bool, int]:
    """
    Fetches group data, checks if user's rank > 1 in all, and formats details for display.
    Assumes group_roles_list and is_data_complete are from get_group_roles_data.

    Returns:
        - detailed_group_string_page2 (str): Formatted string for the group details page.
        - all_ranks_above_one (bool): True if all group ranks are > 1 (for informational purposes on page 2).
        - groups_count (int): Number of groups processed.
    """
    if group_roles_list is None: # Indicates total failure from get_group_roles_data
        return "Could not fetch group details due to an API error.", False, 0

    if not group_roles_list: # User is in no groups
        # is_data_complete doesn't matter much here if the list is empty.
        return "User is not in any groups.", True, 0 # all_ranks_ok is vacuously true

    groups_count = len(group_roles_list)
    all_ranks_ok = True
    offending_groups_for_rank_check = []
    detailed_group_lines_for_page2 = []

    for group_info_item in group_roles_list:
        group_data = group_info_item.get("group", {})
        role_data = group_info_item.get("role", {})

        group_id = group_data.get("id")
        group_name = group_data.get("name", "Unknown Group")
        group_member_count = group_data.get("memberCount", "N/A")
        user_rank_in_group = role_data.get("rank", 0)
        group_link = f"https://www.roblox.com/groups/{group_id}" if group_id else "N/A"

        detailed_group_lines_for_page2.append(
            f"- **{group_name}** ([Link]({group_link}))\n"
            f"  - Members: {group_member_count}, Your Rank ID: {user_rank_in_group}"
        )

        if not (user_rank_in_group > 1):
            all_ranks_ok = False
            offending_groups_for_rank_check.append(f"{group_name} (Rank: {user_rank_in_group})")

    # Message for Page 1 (main check)

    # Build Page 2 content
    page2_content_parts = ["**Group Membership & Ranks:**\n"]
    if detailed_group_lines_for_page2:
        page2_content_parts.extend(detailed_group_lines_for_page2)
    else:
        page2_content_parts.append("No specific group details to display.")

    if not is_data_complete and group_roles_list: # Data was partial and not empty
        page2_content_parts.append("\n\n**Warning:** This group list might be incomplete due to an API error during fetching.")

    return "\n".join(page2_content_parts), all_ranks_ok, groups_count

def check_account_age(user_created_date_str):
    created_date = parse_roblox_date(user_created_date_str)
    return (datetime.utcnow() - created_date).days

def check_xtracker_report(user_id):
    """Check if user has any cheat reports on xTracker."""
    headers = {"Authorization": XTRACKER_API_KEY}
    url = f"https://api.xtracker.xyz/api/registry/user?id={user_id}"
    resp = safe_get(url, headers=headers)
    if not resp:
        return False  # Could not fetch data, treat as no report
    
    data = resp.json()
    # The API returns a list of reports. If list is empty, no reports found.
    return bool(data)

def check_xtracker_ownership(user_id):
    """Check if user owns cheats on xTracker."""
    headers = {"Authorization": XTRACKER_API_KEY}
    url = f"https://api.xtracker.xyz/api/ownership/user?id={user_id}"
    resp = safe_get(url, headers=headers)
    if not resp:
        return False  # Could not fetch data, treat as no cheats owned
    
    data = resp.json()
    return bool(data)



def get_badge_dates(user_id):
    # Fetches all badge metadata, then their awarded dates.
    # Returns a tuple: (parsed_date_list, total_badge_metadata_count)
    # - parsed_date_list: List of datetime.date objects, or None if a critical API error occurred.
    # - total_badge_metadata_count: Integer count of badges found.

    all_badge_metadata = []
    limit = 100 # Changed to an allowed value, max is 100
    cursor = None
    initial_metadata_call_failed = False

    # 1. Fetch all badge metadata (primarily for their IDs)
    print(f"Fetching all badge metadata for user {user_id}...")
    page_num = 0 # For logging
    while True:
        page_num += 1
        # Using the proxy API for fetching badge list
        url = f"{ROBLOX_BADGES_PROXY_API}/users/{user_id}/badges?limit={limit}&sortOrder=Desc"
        if cursor:
            url += f"&cursor={cursor}"
        
        print(f"Fetching badge metadata page {page_num} for user {user_id} from {url}")
        resp = safe_get(url)
        if not resp:
            print(f"Warning: Failed to fetch badge metadata page {page_num} for user {user_id} from {url} (safe_get returned None). Badge metadata list will be incomplete.")
            if not all_badge_metadata:
                initial_metadata_call_failed = True
            break # Stop collecting metadata
        
        try:
            data = resp.json()
            current_page_data = data.get("data", [])
            if not current_page_data and data.get("nextPageCursor"):
                print(f"Warning: Badge metadata page {page_num} for user {user_id} returned empty data but has a nextPageCursor. Continuing cautiously.")
            
            all_badge_metadata.extend(current_page_data)
            
            if len(all_badge_metadata) % 500 == 0 and current_page_data: # Progress print
                 print(f"Fetched {len(all_badge_metadata)} badge metadata items for user {user_id}...")
            
            prev_cursor = cursor # Store previous cursor for logging if next is None but data was received
            cursor = data.get("nextPageCursor")

            if not cursor:
                if current_page_data:
                    print(f"Finished fetching badge metadata for user {user_id}. No nextPageCursor on page {page_num}. Total metadata items: {len(all_badge_metadata)}")
                else:
                    print(f"Finished fetching badge metadata for user {user_id}. No nextPageCursor and no data on page {page_num} (cursor was {prev_cursor}). Total metadata items: {len(all_badge_metadata)}")
                break
        except requests.exceptions.JSONDecodeError:
            print(f"JSONDecodeError while fetching badge metadata page {page_num} for user {user_id} from {url}, response: {resp.text[:200]}. Badge metadata list will be incomplete.")
            if not all_badge_metadata:
                initial_metadata_call_failed = True
            break # Stop collecting metadata
        
        # If there's a next page, add a small delay before fetching it
        if cursor:
            time.sleep(0.5) # 500ms delay
    
    if initial_metadata_call_failed and not all_badge_metadata:
        print(f"Initial metadata call failed for user {user_id}. No badges found.")
        return None, 0

    if not all_badge_metadata:
        print(f"No badge metadata found for user {user_id} after API calls.")
        return [], 0

    badge_ids = [badge['id'] for badge in all_badge_metadata if 'id' in badge]
    if not badge_ids:
        print(f"No badge IDs extracted from metadata for user {user_id}.")
        return []
    
    print(f"Fetched {len(all_badge_metadata)} badge metadata items. Extracted {len(badge_ids)} badge IDs for user {user_id}.")
    total_badge_metadata_count = len(all_badge_metadata)

    # 2. Fetch awarded dates in batches using the collected badge IDs
    awarded_date_strings = []
    initial_awarded_date_call_failed = False 

    print(f"Fetching awarded dates in batches for user {user_id}...")
    for i in range(0, len(badge_ids), AWARDED_DATES_BATCH_SIZE):
        batch_ids = badge_ids[i:i + AWARDED_DATES_BATCH_SIZE]

        # Add a small delay before each batch request to be gentler on the API,
        # especially for services like roproxy.com that might have stricter rate limits.
        if i > 0: # Don't sleep before the very first batch
            time.sleep(1) # Sleep for 1 second between batch requests
        
        # Using requests' params argument with safe_get
        url_base = f"{ROBLOX_BADGES_PROXY_API}/users/{user_id}/badges/awarded-dates"
        params_dict = {'badgeIds': batch_ids} # requests will handle list of IDs correctly
        resp = safe_get(url_base, params=params_dict)

        if not resp:
            if not awarded_date_strings: # If it's the first batch call for dates that fails
                 initial_awarded_date_call_failed = True
            print(f"Failed to fetch awarded dates batch for user {user_id}, IDs: {batch_ids[:5]}...")
            continue # Try next batch
        
        try:
            data = resp.json()
            for badge_award_info in data.get("data", []):
                if "awardedDate" in badge_award_info:
                    awarded_date_strings.append(badge_award_info["awardedDate"])
            if len(awarded_date_strings) % 500 == 0 and data.get("data"): # Progress print
                print(f"Collected {len(awarded_date_strings)} awarded date strings for user {user_id}...")
        except requests.exceptions.JSONDecodeError:
            print(f"JSONDecodeError while fetching awarded dates for batch, response: {resp.text[:200]}")
            if not awarded_date_strings:
                initial_awarded_date_call_failed = True
            continue

    if initial_awarded_date_call_failed and not awarded_date_strings and badge_ids:
        print(f"Failed to fetch any awarded dates for user {user_id}, though badge IDs were found.")
        return None, total_badge_metadata_count # Return None for dates, but provide count of metadata found

    if not awarded_date_strings:
        print(f"No awarded date strings collected for user {user_id}.")
        return [], total_badge_metadata_count

    print(f"Collected {len(awarded_date_strings)} awarded date strings for user {user_id}. Parsing them now...")
    
    # 3. Parse dates
    date_list = []
    for date_str in awarded_date_strings:
        try:
            date_obj = parse_roblox_date(date_str)
            date_list.append(date_obj.date())
        except ValueError: 
            # parse_roblox_date now prints its own error and re-raises;
            # if we catch it here, it means we want to skip this date.
            print(f"Warning: Skipping unparseable date '{date_str}' for user {user_id} after robust attempt.")
            pass 
            
    if not date_list and awarded_date_strings: 
        print(f"All awarded date strings failed to parse for user {user_id}.")
        return [], total_badge_metadata_count

    print(f"Successfully parsed {len(date_list)} dates for user {user_id}.")
    return date_list, total_badge_metadata_count

def check_user_acceptance(user_id, generate_graph=False): # Added generate_graph flag
    user_info = get_user_info(user_id)
    if not user_info:
        return "❌ Could not fetch user info from Roblox.", None, "Could not fetch user info.", "Unknown User" # page1, graph, page2_group, username

    username = user_info.get('name', str(user_id)) # Get username for graph title
    
    # Fetch badge data once for both criteria and graph
    badge_dates_list, total_badges_found = get_badge_dates(user_id)
    badge_pages = math.ceil(total_badges_found / 30)

    blacklist = get_blacklisted_ids()
    is_blacklisted = str(user_id) in blacklist

    # xTracker checks
    has_xtracker_report = check_xtracker_report(user_id)
    owns_cheats = check_xtracker_ownership(user_id)

    # Clanware check
    clanware_api_success, clanware_result = check_clanware_report(user_id)

    # Group checks using the new helper
    group_roles_list_data, group_data_is_complete = get_group_roles_data(user_id)
    group_details_page2_str, _, actual_groups_count = get_formatted_group_details( # all_ranks_ok from here is for page 2 info only
        group_roles_list_data, group_data_is_complete
    )
    
    created_date_str = user_info.get("created")
    account_age_days = check_account_age(created_date_str) if created_date_str else 0
    friends = get_friends_count(user_id)

    result_lines = [
        f"👤 **Username:** {user_info.get('name')}",
        f"🆔 **User ID:** {user_id}",
        "",
        f"🚫 Blacklisted: {'Yes' if is_blacklisted else 'No'}",
        f"❌ xTracker Reported for Cheats: {'Yes' if has_xtracker_report else 'No'}",
        f"❌ Owns Cheats (xTracker): {'Yes' if owns_cheats else 'No'}",
    ]
    if clanware_api_success:
        if clanware_result: # True if user is flagged (e.g., is_exploiter or is_degenerate is true)
            result_lines.append(f"❌ Clanware Flagged: Yes")
        else: # False if user is not flagged (e.g., API returned 404 or explicit non-flagged status)
            result_lines.append(f"✅ Clanware Flagged: No")
    else:
        result_lines.append(f"⚠️ Clanware Check: {clanware_result}") # Display the error/info message

    result_lines.extend([
        "",
        f"📆 Account Age: {account_age_days} days (Required: 90) → {'✅' if account_age_days >= 90 else '❌'}",
        f"🤝 Friends Count: {friends} (Required: 10) → {'✅' if friends >= 10 else '❌'}",
        f"🏅 Badges: {total_badges_found} total ({badge_pages} pages, Required: 10 pages) → {'✅' if badge_pages >= 10 else '❌'}",
    ])

    if group_roles_list_data is None: # Total failure to get group data
        result_lines.append(f"👥 Groups Count: Error fetching (Required: 2) → ❌")
        result_lines.append(f"⚠️ Could not fetch group data (API error).")
    else:
        groups_check_symbol = '✅' if actual_groups_count >= 2 else '❌'
        result_lines.append(f"👥 Groups Count: {actual_groups_count} (Required: 2) → {groups_check_symbol}")
        if not group_data_is_complete and actual_groups_count > 0: # Only show warning if some groups were fetched but data is incomplete
            result_lines.append(f"⚠️ Group list might be incomplete due to API errors.")
            
    # Determine overall status, considering Clanware API success
    is_negatively_flagged_by_clanware = clanware_api_success and clanware_result
    if is_blacklisted or has_xtracker_report or owns_cheats or is_negatively_flagged_by_clanware:
        result_lines.append("\n⚠️ User is **blacklisted or flagged by xTracker/Clanware** and may be restricted.")
    elif all([
        account_age_days >= 90,
        friends >= 10,
        badge_pages >= 10,
        (actual_groups_count >= 2 if group_roles_list_data is not None else False), # Check count only if data fetch wasn't a total error
        # The 'all_ranks_ok_for_criteria' is now informational for page 2, not a strict pass/fail for page 1's overall status.
    ]):
        result_lines.append("\n✅ User **meets** the acceptance criteria.")
    else:
        result_lines.append("\n❌ User **does NOT meet** the acceptance criteria.")

    text_result_page1 = "\n".join(result_lines)
    graph_buffer = None

    if generate_graph:
        if badge_dates_list is None: # Critical API error
            text_result_page1 += "\n\n⚠️ Failed to retrieve badge data for graph generation (API error)."
        elif not badge_dates_list: # No award dates found/parsed, even if badges exist
            text_result_page1 += "\n\nℹ️ No badge award dates found to generate a graph."
        else:
            graph_buffer = plot_badge_history(badge_dates_list, username)
            if not graph_buffer:
                text_result_page1 += "\n\n⚠️ Could not generate badge graph."

    return text_result_page1, graph_buffer, group_details_page2_str, username

class UserCheckView(discord.ui.View):
    def __init__(self, user_id: int, username: str,
                 page1_embed_desc: str, page2_group_details_desc: str, 
                 graph_bytesio_buffer: io.BytesIO | None):
        super().__init__(timeout=180.0) # View times out after 3 minutes
        self.user_id = user_id
        self.username = username # Needed for graph filename if re-attaching

        self.page1_embed_desc = page1_embed_desc
        self.page2_group_details_desc = page2_group_details_desc
        self.graph_bytesio_buffer = graph_bytesio_buffer # Store the BytesIO object

        self.showing_group_details = False
        self._update_button()

    def _make_page1_embed(self) -> discord.Embed:
        desc = self.page1_embed_desc
        if len(desc) > 4096:
            desc = desc[:4090] + "\n[...]" # Truncate and add indicator
        return discord.Embed(
            title=f"User Check: {self.username} (ID: {self.user_id})", 
            description=desc, 
            color=discord.Color.green()
        )

    def _make_page2_embed(self, description: str) -> discord.Embed:
        # Description is prepared by the caller, including any necessary truncation
        # for the embed part. Overflow is handled by sending followup messages.
        return discord.Embed(
            title=f"Group Details: {self.username} (ID: {self.user_id})", 
            description=description,
            color=discord.Color.blue()
        )

    def _update_button(self):
        # Remove previous button if exists to avoid duplicates on re-adding
        for item in list(self.children): # Iterate over a copy for safe removal
            if isinstance(item, discord.ui.Button) and item.custom_id == "toggle_user_check_details":
                self.remove_item(item)
        
        button = discord.ui.Button(
            label="Show Group Details" if not self.showing_group_details else "Show Main Info",
            style=discord.ButtonStyle.secondary if not self.showing_group_details else discord.ButtonStyle.primary,
            custom_id="toggle_user_check_details",
            row=0
        )
        button.callback = self.toggle_details_callback
        self.add_item(button)

    async def toggle_details_callback(self, interaction: discord.Interaction):
        # This interaction is for the button press
        await interaction.response.defer() # Acknowledge button press

        self.showing_group_details = not self.showing_group_details
        self._update_button() # Update button label/style for the next state

        attachments_to_send = []
        new_embed = None
        followup_messages_to_send = [] # List of strings for followup messages

        if self.showing_group_details:
            # Page 2: Group Details
            full_desc_page2 = self.page2_group_details_desc
            # Define the separator that marks the beginning of the "Overall Group Rank Status"
            separator = "\n\n**Overall Group Rank Status:**"
            
            primary_embed_content = full_desc_page2
            overflow_content_for_followup = ""

            if separator in full_desc_page2:
                parts = full_desc_page2.split(separator, 1)
                group_list_part = parts[0]
                # The overall_status_part includes the separator itself to maintain formatting
                overall_status_part_content = separator + parts[1]

                # If the total content (group list + overall status) is too long for one embed
                if len(full_desc_page2) > 4096:
                    primary_embed_content = group_list_part
                    overflow_content_for_followup = overall_status_part_content
                    
                    # If the group_list_part itself is too long for the embed, truncate it
                    if len(primary_embed_content) > 4096:
                        primary_embed_content = primary_embed_content[:4090] + "\n[...]"
                # else: everything fits, primary_embed_content remains full_desc_page2 (already set)
            
            # Fallback for extremely long content without the expected separator (less likely)
            elif len(full_desc_page2) > 4096:
                 primary_embed_content = full_desc_page2[:4090] + "\n[...]"

            new_embed = self._make_page2_embed(description=primary_embed_content)

            if overflow_content_for_followup:
                # Split the overflow_content (Overall Group Rank Status part) into 2000-char chunks
                for i in range(0, len(overflow_content_for_followup), 2000):
                    followup_messages_to_send.append(overflow_content_for_followup[i:i+2000])
        else: 
            # Page 1: Main Info
            new_embed = self._make_page1_embed() # This handles its own truncation
            if self.graph_bytesio_buffer: # If switching to Page 1 and graph exists
                self.graph_bytesio_buffer.seek(0) # Reset buffer
                new_graph_file = discord.File(self.graph_bytesio_buffer, filename=f"badge_graph_{self.username}_{self.user_id}.png")
                attachments_to_send.append(new_graph_file)

        # Edit the original message sent by the bot
        await interaction.message.edit(embed=new_embed, view=self, attachments=attachments_to_send)

        # Send any followup messages (e.g., the "Overall Group Rank Status" part)
        for msg_content in followup_messages_to_send:
            await interaction.followup.send(content=msg_content)
            await asyncio.sleep(0.5) # Small delay between multiple followup messages

@tree.command(name="check", description="Check Roblox user acceptance criteria. Supports multiple, comma-separated.")
@app_commands.describe(identifiers_str="Comma-separated Roblox user IDs or Usernames to check")
async def check_user(interaction: discord.Interaction, identifiers_str: str):
    loop = asyncio.get_event_loop()
    await interaction.response.defer()

    raw_identifiers = [s.strip() for s in identifiers_str.split(',')]
    identifiers_to_process = [id_str for id_str in raw_identifiers if id_str] # Filter out empty strings

    if not identifiers_to_process:
        await interaction.followup.send("Please provide at least one user ID or username.")
        return

    MAX_USERS_PER_COMMAND = 10 # Limit to prevent abuse/long processing
    if len(identifiers_to_process) > MAX_USERS_PER_COMMAND:
        await interaction.followup.send(f"Please check up to {MAX_USERS_PER_COMMAND} users at a time.")
        return

    for individual_identifier in identifiers_to_process:
        # Resolve identifier to user_id
        user_id, error_message = await loop.run_in_executor(None, resolve_roblox_identifier, individual_identifier)
        if user_id is None:
            await interaction.followup.send(f"❌ For '{individual_identifier}': {error_message}")
            continue

        # Run the blocking function in an executor, now returns more info
        page1_text_content, graph_buffer_bytesio, page2_group_details_text, username_for_graph = await loop.run_in_executor(
            None,
            check_user_acceptance,
            user_id,
            True  # generate_graph=True
        )

        # Prepare initial embed (Page 1)
        page1_embed = discord.Embed(
            title=f"User Check: {username_for_graph} (ID: {user_id})",
            description=page1_text_content,
            color=discord.Color.green()
        )
        
        initial_file_to_send = None
        if graph_buffer_bytesio:
            graph_buffer_bytesio.seek(0) # Reset buffer
            initial_file_to_send = discord.File(graph_buffer_bytesio, filename=f"badge_graph_{username_for_graph}_{user_id}.png")

        # Create the view
        view = UserCheckView(user_id, username_for_graph,
                             page1_text_content, page2_group_details_text, 
                             graph_buffer_bytesio) # Pass BytesIO for potential re-use

        # Prepare the arguments for send
        send_args = {
            "embed": page1_embed,
            "view": view
        }
        if initial_file_to_send:
            send_args["file"] = initial_file_to_send
        # Else, initial_file_to_send is None, and we don't add the 'file' key to send_args

        await interaction.followup.send(**send_args)

        # If there are more identifiers to process, send a thinking message
        if identifiers_to_process.index(individual_identifier) < len(identifiers_to_process) - 1:
            # Add a small delay to avoid Discord rate limits when processing multiple users
            await asyncio.sleep(1) # Wait for 1 second before processing the next user
@tree.command(name="badgegraph", description="Show badge graphs for users. Supports multiple, comma-separated.")
@app_commands.describe(identifiers_str="Comma-separated Roblox user IDs or Usernames to graph")
async def badgegraph(interaction: discord.Interaction, identifiers_str: str):
    loop = asyncio.get_event_loop()
    await interaction.response.defer()

    raw_identifiers = [s.strip() for s in identifiers_str.split(',')]
    identifiers_to_process = [id_str for id_str in raw_identifiers if id_str] # Filter out empty strings

    if not identifiers_to_process:
        await interaction.followup.send("Please provide at least one user ID or username.")
        return

    MAX_USERS_PER_COMMAND = 5 # Limit to prevent abuse/long processing
    if len(identifiers_to_process) > MAX_USERS_PER_COMMAND:
        await interaction.followup.send(f"Please request graphs for up to {MAX_USERS_PER_COMMAND} users at a time.")
        return

    for individual_identifier in identifiers_to_process:
        user_id, error_message = await loop.run_in_executor(None, resolve_roblox_identifier, individual_identifier)
        if user_id is None:
            await interaction.followup.send(f"❌ For '{individual_identifier}': {error_message}")
            continue

        user_info = await loop.run_in_executor(None, get_user_info, user_id)
        if not user_info:
            await interaction.followup.send(f"❌ Could not fetch user info for '{individual_identifier}' (ID: {user_id}).")
            continue
        username = user_info.get("name", str(user_id))
        
        badge_dates_list, _ = await loop.run_in_executor(None, get_badge_dates, user_id)

        if badge_dates_list is None:
            await interaction.followup.send(f"❌ Failed to retrieve badge data for **{username}** ('{individual_identifier}'). API error or restricted access.")
            continue
        if not badge_dates_list:
            await interaction.followup.send(f"❌ No badges with award dates found for **{username}** ('{individual_identifier}').")
            continue

        buf = await loop.run_in_executor(None, plot_badge_history, badge_dates_list, username)
        if not buf:
            await interaction.followup.send(f"❌ Could not generate graph for **{username}** ('{individual_identifier}').")
            continue
            
        file = discord.File(buf, filename=f"badge_graph_{user_id}.png")
        await interaction.followup.send(content=f"Badge history for **{username}** ('{individual_identifier}'):", file=file)

        # If there are more identifiers to process, send a thinking message
        if identifiers_to_process.index(individual_identifier) < len(identifiers_to_process) - 1:
            # Add a small delay to avoid Discord rate limits when processing multiple users
            await asyncio.sleep(1) # Wait for 1 second before processing the next user
@tree.command(name="grouprankdetails", description="Shows detailed group rank info (CAN TAKE A VERY LONG TIME).")
@app_commands.describe(identifier="Roblox user ID or Username to check group rank details for")
async def detailed_group_ranks(interaction: discord.Interaction, identifier: str):
    loop = asyncio.get_event_loop()
    await interaction.response.defer(ephemeral=True) # Defer ephemerally as this can be slow

    user_id, error_message = await loop.run_in_executor(None, resolve_roblox_identifier, identifier)
    if user_id is None:
        await interaction.followup.send(f"❌ For '{identifier}': {error_message}", ephemeral=True)
        return

    user_info = await loop.run_in_executor(None, get_user_info, user_id)
    username = user_info.get("name", str(user_id)) if user_info else identifier

    await interaction.followup.send(f"⏳ Fetching detailed group rank information for **{username}** (ID: {user_id}). This might take a while...", ephemeral=True)

    # This part will be slow
    group_roles_list, _ = await loop.run_in_executor(None, get_group_roles_data, user_id) # Ignore is_complete flag here

    if group_roles_list is None:
        await interaction.edit_original_response(content=f"❌ Could not fetch group list for **{username}**.")
        return
    if not group_roles_list:
        await interaction.edit_original_response(content=f"ℹ️ **{username}** is not in any groups.")
        return

    detailed_lines = [f"**Detailed Group Rank Information for {username} (ID: {user_id}):**\n"]
    for group_info_item in group_roles_list:
        group_data = group_info_item.get("group", {})
        role_data = group_info_item.get("role", {})

        group_id = group_data.get("id")
        group_name = group_data.get("name", "Unknown Group")
        user_rank_in_group = role_data.get("rank", 0)
        group_link = f"https://www.roblox.com/groups/{group_id}" if group_id else "N/A"

        ranks_below_user_str = "N/A (or API error)"
        if group_id:
            # This is the slow part, called for each group
            all_group_ranks = await loop.run_in_executor(None, get_all_rank_values_for_group, group_id)
            if all_group_ranks is not None:
                ranks_below_user_count = sum(1 for r in all_group_ranks if r < user_rank_in_group and r > 0)
                ranks_below_user_str = str(ranks_below_user_count)
        
        detailed_lines.append(
            f"- **{group_name}** ([Link]({group_link}))\n"
            f"  - Your Rank ID: {user_rank_in_group}\n"
            f"  - Ranks Below Yours: {ranks_below_user_str}"
        )
    
    final_message = "\n".join(detailed_lines)
    if len(final_message) > 2000: # Discord message limit
        final_message = final_message[:1990] + "\n[...Output truncated...]"
        
    await interaction.edit_original_response(content=final_message) # Send as a normal followup now



@bot.event
async def on_ready():
    await tree.sync()  # Sync commands with Discord
    # Initial population of the blacklist cache
    print("Bot is ready. Performing initial blacklist cache population...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, get_blacklisted_ids)
    print(f"Logged in as {bot.user}!")
    



app = Flask("")

@app.route("/")
def home():
    return "I'm alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

bot.run(TOKEN)