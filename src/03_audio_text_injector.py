import os
import json
import uuid
import shutil
import cv2
import time
import subprocess
import pyautogui

def get_audio_info(path):
    # Just dummy duration, it will be trimmed to video length anyway
    return {"path": path, "duration": 200000000} # 200s

class CapCutBatch03:
    def __init__(self):
        self.drafts_dir = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\User Data\Projects\com.lveditor.draft")
        self.source_dir = os.path.join(self.drafts_dir, "Headless_02")
        
    def build_and_export(self, project_name, audio_path):
        print(f"--- BATCH 03: Audio, Text & Export ({project_name}) ---")
        
        target_dir = os.path.join(self.drafts_dir, project_name)
        if os.path.exists(target_dir): shutil.rmtree(target_dir)
        shutil.copytree(self.source_dir, target_dir)
        
        # 1. Update Meta
        meta_path = os.path.join(target_dir, "draft_meta_info.json")
        with open(meta_path, 'r', encoding='utf-8') as f: meta = json.load(f)
        meta['draft_name'] = project_name
        with open(meta_path, 'w', encoding='utf-8') as f: json.dump(meta, f, ensure_ascii=False)
            
        # 2. Update Content
        content_path = os.path.join(target_dir, "draft_content.json")
        with open(content_path, 'r', encoding='utf-8') as f: content = json.load(f)
            
        if 'texts' not in content['materials']: content['materials']['texts'] = []
        if 'audios' not in content['materials']: content['materials']['audios'] = []
        
        overall_duration = content.get('duration', 200000000)

        # --- Inject Text Track ---
        text_mat_id = str(uuid.uuid4())
        text_seg_id = str(uuid.uuid4())
        
        # Text Material
        content['materials']['texts'].append({
            "id": text_mat_id,
            "type": "text",
            "content": "<font id=\"\" path=\"\"><color><size>Bob Project Showcase</size></color></font>",
            "text_alpha": 1.0,
            "alignment": 1,
            "layer_weight": 1
        })
        
        # Text Track
        content['tracks'].append({
            "id": str(uuid.uuid4()),
            "type": "text",
            "segments": [{
                "id": text_seg_id,
                "material_id": text_mat_id,
                "source_timerange": {"start": 0, "duration": 5000000},
                "target_timerange": {"start": 0, "duration": 5000000}
            }]
        })
        print("  [+] Text Track Added: 'Bob Project Showcase' (0s - 5s)")

        # --- Inject Audio Track ---
        if os.path.exists(audio_path):
            audio_mat_id = str(uuid.uuid4())
            audio_seg_id = str(uuid.uuid4())
            
            content['materials']['audios'].append({
                "id": audio_mat_id,
                "path": audio_path,
                "duration": overall_duration,
                "type": "audio",
                "name": os.path.basename(audio_path)
            })
            
            content['tracks'].append({
                "id": str(uuid.uuid4()),
                "type": "audio",
                "segments": [{
                    "id": audio_seg_id,
                    "material_id": audio_mat_id,
                    "source_timerange": {"start": 0, "duration": overall_duration},
                    "target_timerange": {"start": 0, "duration": overall_duration}
                }]
            })
            print("  [+] Audio Track Added (BGM applied to full duration)")
        
        with open(content_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False)
            
        # Launch CapCut
        print("  [*] Launching CapCut to project...")
        subprocess.run(["taskkill", "/F", "/IM", "CapCut.exe"], capture_output=True)
        capcut_exe = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\Apps\CapCut.exe")
        subprocess.Popen([capcut_exe])
        
        # UI Macro for Export
        print("  [*] Waiting 15 seconds for UI to render before Export Macro...")
        time.sleep(15)
        print("  [*] Triggering Export (Ctrl+E)...")
        pyautogui.hotkey('ctrl', 'e')
        time.sleep(3)
        print("  [*] Starting Render (Enter)...")
        pyautogui.press('enter')
        print("\n=== EXECUTION LOG (Batch 03) ===")
        print("Text Track      : Injected (First 5s)")
        print("Audio Track     : Injected (Full Duration)")
        print("Export Strategy : Render Initiated")
        print("================================")

if __name__ == "__main__":
    engine = CapCutBatch03()
    audio_path = r"D:\ط§ظ„ظ…ط´ط§ط±ظٹط¹\remotion\public\music\spiral.mp3"
    engine.build_and_export("Headless_03", audio_path)

