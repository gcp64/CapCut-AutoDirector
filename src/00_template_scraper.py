import os
import json

drafts_dir = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\User Data\Projects\com.lveditor.draft")

db = {
    "animations": {},
    "text_templates": {},
    "video_effects": {},
    "transitions": {}
}

for proj_name in os.listdir(drafts_dir):
    proj_path = os.path.join(drafts_dir, proj_name)
    content_path = os.path.join(proj_path, "draft_content.json")
    
    if os.path.isfile(content_path):
        try:
            with open(content_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            
            materials = content.get("materials", {})
            
            # Scrape Animations
            for anim in materials.get("material_animations", []):
                for a in anim.get("animations", []):
                    name = a.get("name", "Unknown Anim")
                    if name not in db["animations"]:
                        db["animations"][name] = a
                        
            # Scrape Text Templates
            for txt in materials.get("text_templates", []):
                name = txt.get("name", "Unknown Text Template")
                if name not in db["text_templates"]:
                    db["text_templates"][name] = txt
                    
            # Scrape Video Effects
            for eff in materials.get("video_effects", []):
                name = eff.get("name", "Unknown Effect")
                if name not in db["video_effects"]:
                    db["video_effects"][name] = eff
                    
            # Scrape Transitions
            for trans in materials.get("transitions", []):
                name = trans.get("name", "Unknown Transition")
                if name not in db["transitions"]:
                    db["transitions"][name] = trans
                    
        except Exception as e:
            print(f"Error reading {proj_name}: {e}")

db_path = r"D:\ط§ظ„ظ…ط´ط§ط±ظٹط¹\ظƒط§ط¨ ظƒط§طھ\CapCut_Templates_DB.json"
with open(db_path, 'w', encoding='utf-8') as f:
    json.dump(db, f, indent=4, ensure_ascii=False)

print(f"Scraped Data from all projects:")
print(f"  - Animations     : {len(db['animations'])}")
print(f"  - Text Templates : {len(db['text_templates'])}")
print(f"  - Video Effects  : {len(db['video_effects'])}")
print(f"  - Transitions    : {len(db['transitions'])}")
print(f"Database saved to: {db_path}")

# Print some names if available
if db['animations']: print(f"Sample Animation: {list(db['animations'].keys())[0]}")
if db['video_effects']: print(f"Sample Effect: {list(db['video_effects'].keys())[0]}")

