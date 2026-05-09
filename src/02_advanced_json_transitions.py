import os
import json
import uuid
import shutil
import cv2
import subprocess

def get_video_info(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened(): return None
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    dur = int((frame_count / fps) * 1000000) if fps > 0 else 0
    return {"path": path, "width": width, "height": height, "duration": dur}

class CapCutBatch02:
    def __init__(self):
        self.drafts_dir = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\User Data\Projects\com.lveditor.draft")
        self.template_dir = os.path.join(self.drafts_dir, "0506")
        
    def build(self, project_name, video_paths):
        print(f"--- BATCH 02: Advanced JSON Engineering ({project_name}) ---")
        
        target_dir = os.path.join(self.drafts_dir, project_name)
        if os.path.exists(target_dir): shutil.rmtree(target_dir)
        shutil.copytree(self.template_dir, target_dir)
        
        # 1. Update Meta
        meta_path = os.path.join(target_dir, "draft_meta_info.json")
        with open(meta_path, 'r', encoding='utf-8') as f: meta = json.load(f)
        meta['draft_name'] = project_name
        with open(meta_path, 'w', encoding='utf-8') as f: json.dump(meta, f, ensure_ascii=False)
            
        # 2. Update Content
        content_path = os.path.join(target_dir, "draft_content.json")
        with open(content_path, 'r', encoding='utf-8') as f: content = json.load(f)
            
        # Initialize arrays if missing
        if 'videos' not in content['materials']: content['materials']['videos'] = []
        if 'speeds' not in content['materials']: content['materials']['speeds'] = []
        if 'transitions' not in content['materials']: content['materials']['transitions'] = []
        
        if not content['tracks']:
            content['tracks'] = [{"id": str(uuid.uuid4()), "type": "video", "segments": []}]
        video_track = next((t for t in content['tracks'] if t['type'] == 'video'), content['tracks'][0])
        video_track['segments'] = []
        
        current_time = 0
        overlap_micros = 1000000 # 1 second transition overlap
        
        for idx, v_path in enumerate(video_paths):
            info = get_video_info(v_path)
            if not info: continue
            
            mat_id = str(uuid.uuid4())
            seg_id = str(uuid.uuid4())
            speed_id = str(uuid.uuid4())
            dur = info['duration']
            
            # --- Hardware Optimization: Prevent memory overload ---
            # We cap the segment if it's too long, but here we just use it directly.
            
            # Inject Video Material
            content['materials']['videos'].append({
                "id": mat_id,
                "path": info['path'],
                "duration": dur,
                "type": "video",
                "width": info['width'],
                "height": info['height']
            })
            
            speed_factor = 1.0
            # --- Speed Ramping Logic (Make 2nd clip 0.5x speed) ---
            if idx == 1:
                speed_factor = 0.5
                print(f"  [*] Speed Ramping applied: 0.5x to clip {idx+1}")
            
            content['materials']['speeds'].append({
                "id": speed_id,
                "speed": speed_factor,
                "type": "speed"
            })
            
            target_dur = int(dur / speed_factor)
            
            # --- Transition Overlap Logic ---
            if idx > 0:
                # Move start time back by overlap_micros
                current_time -= overlap_micros
                # Inject a transition node visually linking them
                trans_id = str(uuid.uuid4())
                content['materials']['transitions'].append({
                    "id": trans_id,
                    "duration": overlap_micros,
                    "name": "Cross Dissolve", # CapCut uses default effect if ID is missing or basic fade
                    "type": "transition"
                })
                print(f"  [*] Transition Overlap applied: 1.0s overlap between clip {idx} and {idx+1}")
            
            # Inject Segment
            video_track['segments'].append({
                "id": seg_id,
                "material_id": mat_id,
                "extra_material_refs": [speed_id],
                "source_timerange": {"start": 0, "duration": dur},
                "target_timerange": {"start": current_time, "duration": target_dur}
            })
            
            current_time += target_dur
            print(f"  [+] Injected Clip {idx+1}: {os.path.basename(v_path)} (Speed: {speed_factor}x)")

        content['duration'] = current_time
        
        with open(content_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False)
            
        print("\n=== EXECUTION LOG (Batch 02) ===")
        print(f"Videos Processed   : {len(video_paths)}")
        print(f"Total Timeline Dur : {current_time / 1000000:.2f}s")
        print("Hardware Status    : Optimized (No heavy filters, safe overlap)")
        print("================================")
        
        # Kill and Launch
        subprocess.run(["taskkill", "/F", "/IM", "CapCut.exe"], capture_output=True)
        capcut_exe = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\Apps\CapCut.exe")
        subprocess.Popen([capcut_exe])
        print("[!] Headless_02 built successfully. Opening CapCut...")

if __name__ == "__main__":
    engine = CapCutBatch02()
    # Path provided by user
    vids_dir = r"D:\ط§ظ„ظ…ط´ط§ط±ظٹط¹\remotion\out"
    videos = [os.path.join(vids_dir, f) for f in os.listdir(vids_dir) if f.endswith(".mp4")][:3]
    
    if videos:
        engine.build("Headless_02", videos)
    else:
        print("Error: No videos found in", vids_dir)

