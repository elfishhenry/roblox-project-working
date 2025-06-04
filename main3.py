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
from typing import Optional

load_dotenv()

TOKEN = os.getenv("TOKEN")
SPREADSHEET_ID = "1r44AVDsu8qQ74MUaPSZIDGIHDo6GgF_qpUaMAC5OxXs"

SERVICE_ACCOUNT_INFO = {
    # ... your full service account dict here (keep it the same)
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
    sheet = client.open_by_key(SPREADSHEET_ID).get_worksheet(1)  # second sheet (index 1)
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

def get_user_info(user_id):
    url = f"{ROBLOX_USERS_API}/users/{user_id}"
    resp = safe_get(url)
    return resp.json() if resp else None

def get_user_id_by_username(username) -> Optional[int]:
    url = f"https://users.roblox.com/v1/usernames/users"
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
    pages = badge_count // 30  # 30 badges per page
    return pages, badge_count

def get_groups_count(user_id):
    url = f"{ROBLOX_GROUPS_API}/users/{user_id}/groups/roles"
    resp = safe_get(url)
    return len(resp.json().get("data", [])) if resp else 0

def check_account_age(user_created_date_str):
    created_date = parse_roblox_date(user_created_date_str)
    return (datetime.utcnow() - created_date).days

def get_xtracker_evidence(user_id):
    # Example endpoint - replace with your actual XTracker API if different
    url = f"https://api.xtracker.io/v1/evidence/{user_id}"
    resp = safe_get(url)
    if not resp:
        return None

    data = resp.json()
    # Assume data['evidence'] is a list, pick the last item if exists
    evidence_list = data.get("evidence", [])
    if not evidence_list:
        return None

    last_evidence = evidence_list[-1]
    # Example fields, adjust to your actual API response
    date_str = last_evidence.get("date")  # e.g. "2024-07-13T00:00:00Z"
    proof_type = last_evidence.get("type")  # e.g. "Alt Proof"
    linked_user = last_evidence.get("linkedUser")  # e.g. "lightasrm"
    tracker_linked_user = last_evidence.get("trackerLinkedUser")  # e.g. "southsouljah"

    # Format date nicely
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        date_formatted = dt.strftime("%m/%d/%Y %I:%M:%S %p")
    except Exception:
        date_formatted = date_str

    return f"Yes, last evidence on {date_formatted} for {proof_type} | Linking {linked_user} :trackerLink: {tracker_linked_user}"

# Then, inside check_user_acceptance(), after the other checks, add:

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

    # Add XTracker evidence check:
    evidence_text = get_xtracker_evidence(user_id)
    if evidence_text:
        result_lines.append("\nXTracker Evidence?\n" + evidence_text)

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

    user_inputs = users.split()
    results = []

    for user_input in user_inputs:
        user_id = None
        if user_input.isdigit():
            user_id = int(user_input)
        else:
            user_id = get_user_id_by_username(user_input)
            if user_id is None:
                results.append(f"❌ Could not find user ID for username `{user_input}`.")
                continue

        result = check_user_acceptance(user_id)
        results.append(result)

    final_message = "\n\n".join(results)

    # Discord message max length is 2000, so split if needed
    if len(final_message) > 1900:
        chunks = [final_message[i:i+1900] for i in range(0, len(final_message), 1900)]
        for chunk in chunks:
            await interaction.followup.send(chunk)
    else:
        await interaction.followup.send(final_message)

@bot.event
async def on_ready():
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
