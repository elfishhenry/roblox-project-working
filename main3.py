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

load_dotenv()

# Discord token (still recommended to keep token in .env or environment variable)
TOKEN = os.getenv("TOKEN")

# New Spreadsheet ID from your provided Google Sheets link
SPREADSHEET_ID = "1r44AVDsu8qQ74MUaPSZIDGIHDo6GgF_qpUaMAC5OxXs"

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
ROBLOX_GROUPS_API = "https://groups.roblox.com/v2"

# Setup Discord bot
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
    

def safe_get(url, max_retries=3, backoff_factor=1):
    for attempt in range(max_retries):
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            return resp
        except (ConnectionError, HTTPError):
            if attempt == max_retries - 1:
                return None
            time.sleep(backoff_factor * (2 ** attempt))

def parse_roblox_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

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

def get_badges_count(user_id):
    badges = []
    limit = 100
    cursor = None
    while True:
        url = f"{ROBLOX_BADGES_API}/users/{user_id}/badges?limit={limit}"
        if cursor:
            url += f"&cursor={cursor}"
        resp = safe_get(url)
        if not resp:
            break
        data = resp.json()
        badges.extend(data.get("data", []))
        cursor = data.get("nextPageCursor")
        if not cursor:
            break
    return len(badges)

def get_groups_count(user_id):
    url = f"{ROBLOX_GROUPS_API}/users/{user_id}/groups/roles"
    resp = safe_get(url)
    return len(resp.json().get("data", [])) if resp else 0

def get_xtracker_evidence(user_id):
    # TODO: Replace this stub with real XTracker data retrieval
    # Return None if no evidence
    # Return dict with keys: date, proof_type, linking_user, tracker_emoji, linked_user

    # Example hardcoded data for demonstration:
    if str(user_id) == "123456789":
        return {
            "date": "2024-07-13T00:00:00Z",
            "proof_type": "Alt Proof",
            "linking_user": "lightasrm",
            "tracker_emoji": ":trackerLink:",
            "linked_user": "southsouljah"
        }
    return None

@tree.command(name="checkacceptance", description="Check acceptance criteria of a Roblox user by ID or username")
@app_commands.describe(user="Roblox user ID or username")
async def checkacceptance(interaction: discord.Interaction, user: str):
    await interaction.response.defer()  # defer reply for long operations

    # Determine if input is a user ID (digits) or username (string)
    user_id = None
    if user.isdigit():
        user_id = int(user)
    else:
        # Lookup by username to get user ID
        url = f"{ROBLOX_USERS_API}/users/get-by-username?username={user}"
        resp = safe_get(url)
        if not resp or resp.status_code != 200:
            await interaction.followup.send(f"User `{user}` not found.")
            return
        user_id = resp.json().get("Id")
        if not user_id:
            await interaction.followup.send(f"User `{user}` not found.")
            return

    # Blacklist check
    blacklisted_ids = get_blacklisted_ids()
    is_blacklisted = str(user_id) in blacklisted_ids

    user_info = get_user_info(user_id)
    if not user_info:
        await interaction.followup.send(f"Failed to fetch data for user ID `{user_id}`.")
        return

    # Account age calculation
    created_str = user_info.get("created")
    created_date = parse_roblox_date(created_str) if created_str else None
    account_age_days = (datetime.utcnow() - created_date).days if created_date else 0

    friends = get_friends_count(user_id)
    badges = get_badges_count(user_id)
    groups = get_groups_count(user_id)

    # Acceptance criteria thresholds
    required_account_age = 90
    required_friends = 10
    required_badges = 10
    required_groups = 2

    result_lines = [
        f"👤 **Username:** {user_info.get('name')}",
        f"🆔 **User ID:** {user_id}",
        "",
        f"🚫 Blacklisted: {'Yes' if is_blacklisted else 'No'}",
        "",
        f"📆 Account Age: {account_age_days} days (Required: {required_account_age}) → {'✅' if account_age_days >= required_account_age else '❌'}",
        f"🤝 Friends Count: {friends} (Required: {required_friends}) → {'✅' if friends >= required_friends else '❌'}",
        f"🏅 Badges Count: {badges} (Required: {required_badges}) → {'✅' if badges >= required_badges else '❌'}",
        f"👥 Groups Count: {groups} (Required: {required_groups}) → {'✅' if groups >= required_groups else '❌'}",
    ]

    # Add XTracker evidence info
    evidence = get_xtracker_evidence(user_id)
    if evidence:
        dt = datetime.strptime(evidence["date"], "%Y-%m-%dT%H:%M:%SZ")
        formatted_date = dt.strftime("%m/%d/%Y %I:%M:%S %p")

        xtracker_line = (
            f"XTracker Evidence?\n"
            f"Yes, last evidence on {formatted_date} for {evidence['proof_type']} | "
            f"Linking {evidence['linking_user']} {evidence['tracker_emoji']} {evidence['linked_user']}"
        )
    else:
        xtracker_line = "XTracker Evidence?\nNo"

    result_lines.append("")
    result_lines.append(xtracker_line)

    result_text = "\n".join(result_lines)

    await interaction.followup.send(f"```{result_text}```")

bot.run(TOKEN)
