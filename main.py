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


load_dotenv()

# Discord token (still recommended to keep token in .env or environment variable)
TOKEN = os.getenv("TOKEN")
XTRACKER_API_KEY = os.getenv("XTRACKER_API_KEY")
CLANWARE_API_KEY = os.getenv("CLANWARE_API_KEY")


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

# Setup Google Sheets client
def get_blacklisted_ids():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
    client = gspread.authorize(creds)
    print("blacklisted checked")
    sheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(1)  # second sheet (index 1)
    blacklist_column = sheet.col_values(4)  # Column D
    return set(filter(str.isdigit, blacklist_column))  # Only numeric IDs
    

def safe_get(url, params=None, max_retries=3, backoff_factor=1, headers=None): # Added params argument
    for attempt in range(max_retries):
        try:
            # Added timeout and more detailed logging for errors
            print(f"safe_get: Attempt {attempt + 1} for {url} with params {params}") 
            resp = requests.get(url, params=params, headers=headers, timeout=10) # Used params
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

def check_clanware_report(user_id: int) -> tuple[bool, bool | str]:
    """
    Checks if a user is flagged by the Clanware API.

    Returns:
        A tuple (api_call_successful: bool, result: bool | str).
        If api_call_successful is True, result is a boolean indicating if the user is flagged.
        If api_call_successful is False, result is a string message explaining the issue.
    """
    if not CLANWARE_API_KEY:
        print("Warning: CLANWARE_API_KEY is not set. Clanware check will be skipped.")
        return False, "Clanware API key not configured. Check skipped."

    # Reverted to the older Clanware API endpoint
    headers = {"Authorization": CLANWARE_API_KEY}
    url = f"https://api.clanware.xyz/user/check?id={user_id}"
    
    print(f"Checking Clanware for user ID: {user_id} at {url}")
    response = safe_get(url, headers=headers)

    if response is None:
        # safe_get logs detailed errors (e.g., NameResolutionError leading to ConnectionError)
        # Also, if the API key is wrong or endpoint changed, safe_get might return None after retries for 401/403/404
        return False, "Could not connect to Clanware API. Please check manually."

    try:
        data = response.json()
        
        is_flagged = data.get("isFlagged") # Get value, could be None if key is missing
        
        if is_flagged is None:
            print(f"Clanware API response for user {user_id} missing 'isFlagged' field. Response: {data}")
            return False, "Clanware API response format unexpected (missing 'isFlagged'). Please check manually."
        
        if not isinstance(is_flagged, bool):
            print(f"Clanware API response for user {user_id} 'isFlagged' is not a boolean. Value: {is_flagged}, Type: {type(is_flagged)}. Response: {data}")
            return False, "Clanware API response format unexpected ('isFlagged' not boolean). Please check manually."

        print(f"Clanware check successful for user ID: {user_id}. Flagged: {is_flagged}")
        return True, is_flagged

    except requests.exceptions.JSONDecodeError:
        print(f"Error decoding Clanware API JSON response for user {user_id}. Response text: {response.text[:200]}")
        return False, "Error decoding Clanware API response. Please check manually."
    except Exception as e: # Catch any other unexpected errors during processing
        print(f"Unexpected error processing Clanware response for user {user_id}: {e}")
        return False, "An unexpected error occurred with the Clanware check. Please check manually."

def get_groups_count(user_id):
    url = f"{ROBLOX_GROUPS_API}/users/{user_id}/groups/roles"
    resp = safe_get(url)
    return len(resp.json().get("data", [])) if resp else 0

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
    limit = 100
    cursor = None
    initial_metadata_call_failed = False

    # 1. Fetch all badge metadata (primarily for their IDs)
    print(f"Fetching all badge metadata for user {user_id}...")
    while True:
        # Using the proxy API for fetching badge list
        url = f"{ROBLOX_BADGES_PROXY_API}/users/{user_id}/badges?limit={limit}&sortOrder=Desc"
        if cursor:
            url += f"&cursor={cursor}"
        
        resp = safe_get(url)
        if not resp:
            if not all_badge_metadata:
                initial_metadata_call_failed = True
            break
        
        try:
            data = resp.json()
            current_page_data = data.get("data", [])
            all_badge_metadata.extend(current_page_data)
            if len(all_badge_metadata) % 500 == 0 and current_page_data: # Progress print
                 print(f"Fetched {len(all_badge_metadata)} badge metadata items for user {user_id}...")
            cursor = data.get("nextPageCursor")
            if not cursor:
                break
        except requests.exceptions.JSONDecodeError:
            print(f"JSONDecodeError while fetching badge metadata from {url}, response: {resp.text[:200]}")
            if not all_badge_metadata:
                initial_metadata_call_failed = True
            break
    
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
        return "❌ Could not fetch user info from Roblox.", None # Return tuple

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

    created_date_str = user_info.get("created")
    account_age_days = check_account_age(created_date_str) if created_date_str else 0
    friends = get_friends_count(user_id)
    groups = get_groups_count(user_id)
    # badges variable is now total_badges_found

    result_lines = [
        f"👤 **Username:** {user_info.get('name')}",
        f"🆔 **User ID:** {user_id}",
        "",
        f"🚫 Blacklisted: {'Yes' if is_blacklisted else 'No'}",
        f"❌ xTracker Reported for Cheats: {'Yes' if has_xtracker_report else 'No'}",
        f"❌ Owns Cheats (xTracker): {'Yes' if owns_cheats else 'No'}",
    ]
    if clanware_api_success:
        result_lines.append(f"❌ Clanware Flagged: {'Yes' if clanware_result else 'No'}")
    else:
        result_lines.append(f"⚠️ Clanware Check: {clanware_result}") # Display the error/info message

    result_lines.extend([
        "",
        f"📆 Account Age: {account_age_days} days (Required: 90) → {'✅' if account_age_days >= 90 else '❌'}",
        f"🤝 Friends Count: {friends} (Required: 10) → {'✅' if friends >= 10 else '❌'}",
        f"🏅 Badges: {total_badges_found} total ({badge_pages} pages, Required: 10 pages) → {'✅' if badge_pages >= 10 else '❌'}",
        f"👥 Groups Count: {groups} (Required: 2) → {'✅' if groups >= 2 else '❌'}",
    ])

    # Determine overall status, considering Clanware API success
    is_negatively_flagged_by_clanware = clanware_api_success and clanware_result
    if is_blacklisted or has_xtracker_report or owns_cheats or is_negatively_flagged_by_clanware:
        result_lines.append("\n⚠️ User is **blacklisted or flagged by xTracker/Clanware** and may be restricted.")
    elif all([
        account_age_days >= 90,
        friends >= 10,
        badge_pages >= 10,
        groups >= 2,
    ]):
        result_lines.append("\n✅ User **meets** the acceptance criteria.")
    else:
        result_lines.append("\n❌ User **does NOT meet** the acceptance criteria.")

    text_result = "\n".join(result_lines)
    graph_buffer = None

    if generate_graph:
        if badge_dates_list is None: # Critical API error
            text_result += "\n\n⚠️ Failed to retrieve badge data for graph generation (API error)."
        elif not badge_dates_list: # No award dates found/parsed, even if badges exist
            text_result += "\n\nℹ️ No badge award dates found to generate a graph."
        else:
            graph_buffer = plot_badge_history(badge_dates_list, username)
            if not graph_buffer:
                text_result += "\n\n⚠️ Could not generate badge graph."

    return text_result, graph_buffer

@tree.command(name="check", description="Check Roblox user acceptance criteria by ID")
@app_commands.describe(user_id="Roblox user ID to check")
async def check_user(interaction: discord.Interaction, user_id: int):
    loop = asyncio.get_event_loop()
    await interaction.response.defer()

    # Run the blocking function in an executor
    text_result, graph_buffer = await loop.run_in_executor(
        None,  # Uses the default ThreadPoolExecutor
        check_user_acceptance,  # The function to run
        user_id,  # Arguments for the function
        True  # generate_graph=True
    )

    if graph_buffer:
        file = discord.File(graph_buffer, filename="badge_graph.png")
        await interaction.followup.send(content=text_result, file=file)
    else:
        await interaction.followup.send(text_result)

@tree.command(name="badgegraph", description="Show a graph of a Roblox user's badge history by user ID")
@app_commands.describe(user_id="Roblox user ID to graph")
async def badgegraph(interaction: discord.Interaction, user_id: int):
    loop = asyncio.get_event_loop()
    await interaction.response.defer()

    # Run blocking functions in an executor
    user_info = await loop.run_in_executor(None, get_user_info, user_id)
    if not user_info:
        await interaction.followup.send(f"❌ Could not fetch user info for Roblox ID {user_id}. The user may not exist or the Roblox API is unavailable.")
        return
    username = user_info.get("name", str(user_id))
    
    badge_dates_list, _ = await loop.run_in_executor(None, get_badge_dates, user_id) # We only need the list of dates here

    # plot_badge_history is CPU-bound (matplotlib) and also involves BytesIO,
    # so it's good to run in an executor too if it becomes complex or slow.
    # For now, let's assume it's quick enough after badge_dates is fetched.

    if badge_dates_list is None:
        # API call failed critically before any badge data could be processed
        await interaction.followup.send(f"❌ Failed to retrieve badge data for **{username}**. Roblox API might be temporarily unavailable, access could be restricted (e.g., private inventory leading to an error), or another API issue occurred.")
        return
    if not badge_dates_list:
        # API call succeeded (or partially), but no badges with dates found
        await interaction.followup.send(f"❌ No badges with award dates found for **{username}**. They might have no badges, their badges lack award dates, or their badge inventory is private and returns empty data.")
        return

    buf = await loop.run_in_executor(None, plot_badge_history, badge_dates_list, username)
    if not buf:
        await interaction.followup.send("❌ Could not generate graph.")
        return
    file = discord.File(buf, filename="badge_graph.png")
    await interaction.followup.send(content=f"Badge history for **{username}**:", file=file)



@bot.event
async def on_ready():
    await tree.sync()  # Sync commands with Discord
    print(f"Logged in as {bot.user}!")

from flask import Flask
import threading

app = Flask("")

@app.route("/")
def home():
    return "I'm alive!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

bot.run(TOKEN)