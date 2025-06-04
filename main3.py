import discord
from discord.ext import commands
from discord import app_commands
import json
import requests
import time
from datetime import datetime, timezone, timedelta
from requests.exceptions import ConnectionError, HTTPError
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

TOKEN = os.getenv("TOKEN")
SPREADSHEET_ID = "1r44AVDsu8qQ74MUaPSZIDGIHDo6GgF_qpUaMAC5OxXs"

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

ROBLOX_USERS_API = "https://users.roblox.com/v1"
ROBLOX_FRIENDS_API = "https://friends.roblox.com/v1"
ROBLOX_BADGES_API = "https://badges.roblox.com/v1"
ROBLOX_GROUPS_API = "https://groups.roblox.com/v2"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

def get_blacklisted_ids():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(1)
    blacklist_column = sheet.col_values(4)  # Column D
    return set(filter(str.isdigit, blacklist_column))

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

def get_current_date_discord_timestamp():
    SAST = timezone(timedelta(hours=2))
    now_sast = datetime.now(SAST)
    now_utc = now_sast.astimezone(timezone.utc)
    unix_timestamp = int(now_utc.timestamp())
    return f"<t:{unix_timestamp}:F>"

def get_user_info(user_id):
    url = f"{ROBLOX_USERS_API}/users/{user_id}"
    resp = safe_get(url)
    return resp.json() if resp else None

def get_user_id_by_username(username) -> Optional[int]:
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {"usernames": [username], "excludeBannedUsers": True}
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if "data" in data and len(data["data"]) > 0:
            return data["data"][0]["id"]
    except Exception:
        pass
    return None

def get_friends_count(user_id):
    url = f"{ROBLOX_FRIENDS_API}/users/{user_id}/friends/count"
    resp = safe_get(url)
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

def get_badge_pages(user_id):
    badge_count = get_badges_count(user_id)
    pages = badge_count // 30
    return pages, badge_count

def get_groups_count(user_id):
    url = f"{ROBLOX_GROUPS_API}/users/{user_id}/groups/roles"
    resp = safe_get(url)
    return len(resp.json().get("data", [])) if resp else 0

def check_account_age(user_created_date_str):
    created_date = parse_roblox_date(user_created_date_str)
    return (datetime.utcnow() - created_date).days

def get_xtracker_evidence(user_id):
    url = f"https://api.xtracker.io/v1/evidence/{user_id}"
    resp = safe_get(url)
    if not resp:
        return None

    data = resp.json()
    evidence_list = data.get("evidence", [])
    if not evidence_list:
        return None

    last_evidence = evidence_list[-1]
    date_str = last_evidence.get("date")
    proof_type = last_evidence.get("type")
    linked_user = last_evidence.get("linkedUser")
    tracker_linked_user = last_evidence.get("trackerLinkedUser")

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        date_formatted = dt.strftime("%m/%d/%Y %I:%M:%S %p")
    except Exception:
        date_formatted = date_str

    return f"Yes, last evidence on {date_formatted} for {proof_type} | Linking {linked_user} :trackerLink: {tracker_linked_user}"

def check_user_acceptance(user_id):
    user_info = get_user_info(user_id)
    if not user_info:
        return f"❌ Could not fetch user info for ID {user_id}."

    blacklist = get_blacklisted_ids()
    is_blacklisted = str(user_id) in blacklist

    created_date_str = user_info.get("created")
    account_age_days = check_account_age(created_date_str) if created_date_str else 0
    friends = get_friends_count(user_id)
    badge_pages, badges = get_badge_pages(user_id)
    groups = get_groups_count(user_id)

    result_lines = [
        f"👤 **Username:** {user_info.get('name')}",
        f"🆔 **User ID:** {user_id}",
        "",
        f"🚫 Blacklisted: {'Yes' if is_blacklisted else 'No'}",
        "",
        f"📆 Account Age: {account_age_days} days (Required: 90) → {'✅' if account_age_days >= 90 else '❌'}",
        f"🤝 Friends Count: {friends} (Required: 10) → {'✅' if friends >= 10 else '❌'}",
        f"🏅 Badges Count: {badges} (Required: 10) → {'✅' if badges >= 10 else '❌'}",
        f"📄 Badge Pages (30 per page): {badge_pages}",
        f"👥 Groups Count: {groups} (Required: 2) → {'✅' if groups >= 2 else '❌'}",
    ]

    evidence_text = get_xtracker_evidence(user_id)
    if evidence_text:
        result_lines.append("\nXTracker Evidence?\n" + evidence_text)
    else:
        result_lines.append("\nXTracker Evidence?\nNo evidence found.")

    current_date = get_current_date_discord_timestamp()
    result_lines.append(f"\nCurrent date: {current_date}")

    if is_blacklisted:
        result_lines.append("\n⚠️ User is **blacklisted** and may be restricted.")
    elif all([
        account_age_days >= 90,
        friends >= 10,
        badges >= 10,
        groups >= 2,
    ]):
        result_lines.append("\n✅ User **meets** the acceptance criteria.")
    else:
        result_lines.append("\n❌ User **does NOT meet** the acceptance criteria.")

    return "\n".join(result_lines)

@tree.command(name="check", description="Check multiple Roblox users by username or ID (space separated)")
@app_commands.describe(users="Usernames or IDs separated by spaces")
async def check_user(interaction: discord.Interaction, users: str):
    await interaction.response.defer()
    user_list = users.split()
    results = []

    for u in user_list:
        if u.isdigit():
            user_id = int(u)
        else:
            user_id = get_user_id_by_username(u)
            if not user_id:
                results.append(f"❌ Could not find user `{u}`.")
                continue
        result = check_user_acceptance(user_id)
        results.append(result)
        results.append("---")

    await interaction.followup.send("\n\n".join(results), ephemeral=True)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await tree.sync()

bot.run(TOKEN)
