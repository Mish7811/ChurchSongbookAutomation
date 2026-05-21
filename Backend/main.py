from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from googleapiclient.discovery import build
from google.oauth2 import service_account
import gspread
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Debug: Print to verify .env is loaded
# print("🔍 Debug: Environment variables loaded")
# print(f"SPREADSHEET_ID: {os.environ.get('SPREADSHEET_ID')}")
# print(f"SHEET_NAME: {os.environ.get('SHEET_NAME')}")
# print(f"SLIDES_A_ID: {os.environ.get('SLIDES_A_ID')}")

# ----------------- CONFIG -----------------
SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/spreadsheets'  # Added Sheets scope
]

# Read service account credentials from environment variable
creds_json = os.environ.get("GOOGLE_CREDS_JSON")
if not creds_json:
    raise ValueError("Missing GOOGLE_CREDS_JSON environment variable!")
creds_info = json.loads(creds_json)
creds = service_account.Credentials.from_service_account_info(creds_info, scopes=SCOPES)

# Slot to Slides ID mapping
SLOT_SLIDES_MAP = {
    "A": os.environ.get("SLIDES_A_ID"),
    "B": os.environ.get("SLIDES_B_ID"),
    "C": os.environ.get("SLIDES_C_ID")
}

# Google Sheets configuration
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
SHEET_NAME = os.environ.get("SHEET_NAME", "Feb")  # Default to "Feb"
BATCH_SIZE = 15

# Validate configuration
for slot, slides_id in SLOT_SLIDES_MAP.items():
    if not slides_id:
        raise ValueError(f"Missing SLIDES_{slot}_ID environment variable!")

if not SPREADSHEET_ID:
    raise ValueError("Missing SPREADSHEET_ID environment variable!")

# ----------------- SETUP -----------------
slides_service = build('slides', 'v1', credentials=creds)
sheets_client = gspread.authorize(creds)  # For Google Sheets
app = FastAPI()

# CORS
origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Column indices (0-based)
COLUMNS = {
    "S_NO": 0,
    "TAMIL_TELUGU": 1,
    "ENGLISH": 2,
    "ASSIGNED_SLOT": 3,
    "STATUS": 4
}

# ----------------- HELPER FUNCTIONS -----------------
def get_week_info():
    today = datetime.today()

    # Find this week's Sunday
    days_until_sunday = 6 - today.weekday()
    current_sunday = today + timedelta(days=days_until_sunday)

    # First day of year
    start_of_year = datetime(current_sunday.year, 1, 1)

    # First Sunday of year
    days_until_first_sunday = (6 - start_of_year.weekday()) % 7
    first_sunday = start_of_year + timedelta(days=days_until_first_sunday)

    # Calculate week number
    week_number = (
        (current_sunday - first_sunday).days // 7
    ) + 1

    # Suffix logic
    if 11 <= week_number % 100 <= 13:
        suffix = "th"
    else:
        suffix = {
            1: "st",
            2: "nd",
            3: "rd"
        }.get(week_number % 10, "th")

    return {
        "week_number": str(week_number),
        "week_suffix": suffix
    }

def get_sheet():
    """Get the Google Sheet"""
    try:
        print(f"🔍 Attempting to open spreadsheet: {SPREADSHEET_ID}")
        spreadsheet = sheets_client.open_by_key(SPREADSHEET_ID)
        print(f"✅ Spreadsheet opened: {spreadsheet.title}")
        
        print(f"🔍 Looking for worksheet: {SHEET_NAME}")
        worksheet = spreadsheet.worksheet(SHEET_NAME)
        print(f"✅ Worksheet found: {worksheet.title}")
        
        return worksheet
    except gspread.exceptions.SpreadsheetNotFound as e:
        print(f"❌ Spreadsheet not found: {SPREADSHEET_ID}")
        raise HTTPException(status_code=404, detail=f"Spreadsheet not found. Make sure service account has access to: {SPREADSHEET_ID}")
    except gspread.exceptions.WorksheetNotFound as e:
        print(f"❌ Worksheet '{SHEET_NAME}' not found")
        available = spreadsheet.worksheets()
        sheet_names = [ws.title for ws in available]
        raise HTTPException(status_code=404, detail=f"Worksheet '{SHEET_NAME}' not found. Available worksheets: {', '.join(sheet_names)}")
    except gspread.exceptions.APIError as e:
        print(f"❌ Google Sheets API Error: {e}")
        raise HTTPException(status_code=500, detail=f"Google Sheets API Error: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to access Google Sheet: {type(e).__name__}: {str(e)}")

def build_replacement_map(data: dict):
    """Converts incoming JSON to a flat replacement map"""
    weekly_keys = [
        'BN_offering',
        'MN_offering', 
        'PN_offering', 
        'BN_SundayS', 
        'MN_SundayS', 
        'PN_SundayS'
    ]
    replacement_map = {k: str(data.get(k, '')) for k in weekly_keys}

    # Songs
    songs = data.get('songs', [])
    for idx, song in enumerate(songs):
        song_key = f"song_{idx + 1}"
        replacement_map[song_key] = song.get('main', '')
        replacement_map[f"{song_key}_eng"] = song.get('eng', '')

    return replacement_map

# ----------------- ENDPOINTS -----------------
@app.get("/api/songs")
async def get_songs(slot: str):
    """
    Fetch pending songs for a specific slot from Google Sheets
    """
    if slot not in ["A", "B", "C"]:
        raise HTTPException(status_code=400, detail="Invalid slot. Use A, B, or C.")
    
    try:
        worksheet = get_sheet()
        all_data = worksheet.get_all_values()
        
        if len(all_data) < 2:
            return {"success": True, "slot": slot, "songs": [], "count": 0}
        
        # Skip header row (index 0)
        songs = []
        for i in range(1, len(all_data)):
            row = all_data[i]
            
            # Make sure row has enough columns
            if len(row) <= COLUMNS["STATUS"]:
                continue
                
            assigned_slot = row[COLUMNS["ASSIGNED_SLOT"]]
            status = row[COLUMNS["STATUS"]]
            
            # Only fetch songs for this slot with "pending" status
            if assigned_slot == slot and status.lower() == "pending":
                songs.append({
                    "sno": row[COLUMNS["S_NO"]],
                    "main": row[COLUMNS["TAMIL_TELUGU"]],
                    "eng": row[COLUMNS["ENGLISH"]],
                    "slot": assigned_slot,
                    "rowIndex": i + 1  # 1-indexed for Google Sheets
                })
                # 🔑 STOP after 15 songs
                if len(songs) >= BATCH_SIZE:
                    break
        
        return {
            "success": True,
            "slot": slot,
            "songs": songs,
            "count": len(songs)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch songs: {e}")

@app.post("/update-slides")
async def update_slides(request: Request):
    """
    Update Google Slides for a specific slot and mark songs as done
    """
    try:
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    # Extract slot and validate
    slot = data.get('slot')
    if not slot or slot not in SLOT_SLIDES_MAP:
        raise HTTPException(status_code=400, detail="Invalid or missing slot (A, B, or C)")

    # Get the correct presentation ID for this slot
    presentation_id = SLOT_SLIDES_MAP[slot]
    
    # Extract S.No list for marking done later
    songs = data.get('songs', [])
    sno_list = [str(song['sno']) for song in songs if 'sno' in song]

    # Build replacement map
    replacement_map = build_replacement_map(data)
    week_info = get_week_info()

    replacement_map.update(week_info)

    # Fetch current presentation
    presentation = slides_service.presentations().get(
        presentationId=presentation_id
    ).execute()

    requests_list = []

    # Update slides by alt text matching
    for slide in presentation.get('slides', []):
        for element in slide.get('pageElements', []):
            shape = element.get('shape')
            if not shape:
                continue
            
            alt_desc = element.get('description', '')
            if not alt_desc or alt_desc not in replacement_map:
                continue

            text = replacement_map[alt_desc]
            object_id = element['objectId']
            
            # Delete existing text
            requests_list.append({
                'deleteText': {
                    'objectId': object_id,
                    'textRange': {'type': 'ALL'}
                }
            })
            
            # Insert new text
            requests_list.append({
                'insertText': {
                    'objectId': object_id,
                    'insertionIndex': 0,
                    'text': text
                }
            })

    # Execute batch update on slides
    if requests_list:
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id,
            body={'requests': requests_list}
        ).execute()

        # Mark songs as done in Google Sheets
        if sno_list:
            try:
                print(f"📝 Marking {len(sno_list)} songs as done: {sno_list}")
                worksheet = get_sheet()
                all_data = worksheet.get_all_values()
                
                # Convert sno_list to strings for comparison
                sno_list_str = [str(sno) for sno in sno_list]
                
                updates = []
                for i in range(1, len(all_data)):
                    row = all_data[i]
                    if len(row) > COLUMNS["S_NO"]:
                        sno = str(row[COLUMNS["S_NO"]]).strip()
                        
                        if sno in sno_list_str:
                            # Calculate the cell position (1-indexed)
                            row_num = i + 1
                            col_num = COLUMNS["STATUS"] + 1
                            
                            print(f"   ✓ Updating S.No {sno} at row {row_num}, col {col_num}")
                            updates.append({
                                "row": row_num,
                                "col": col_num,
                                "value": "done"
                            })
                
                # Batch update all status cells
                if updates:
                    print(f"📊 Updating {len(updates)} cells...")
                    for update in updates:
                        worksheet.update_cell(update["row"], update["col"], update["value"])
                    
                    sheet_update_msg = f"{len(updates)} songs marked as done in Google Sheets"
                    print(f"✅ {sheet_update_msg}")
                else:
                    sheet_update_msg = "No matching songs found to update"
                    print(f"⚠️ {sheet_update_msg}")
                    
            except Exception as e:
                print(f"❌ Failed to update sheet status: {e}")
                sheet_update_msg = f"Slides updated but failed to update sheet: {e}"
        else:
            sheet_update_msg = "No songs to mark as done"

        return {
            "status": "success",
            "message": f"Slot {slot} slides updated successfully!",
            "slot": slot,
            "songsUpdated": len(sno_list),
            "sheetUpdate": sheet_update_msg
        }
    else:
        return {
            "status": "warning",
            "message": "No matching alt text found in slides."
        }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "slots": list(SLOT_SLIDES_MAP.keys()),
        "spreadsheet_id": SPREADSHEET_ID,
        "sheet_name": SHEET_NAME
    }
