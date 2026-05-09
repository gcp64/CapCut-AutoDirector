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
    duration_sec = frame_count / fps if fps > 0 else 0
    return {
        "path": path,
        "width": width,
        "height": height,
        "duration_micros": int(duration_sec * 1000000)
    }

def find_videos(limit=3):
    search_paths = [
        r"D:\ظپظٹط¯ظٹظˆ\Screen Recordings",
        r"C:\path\to\your\videos",
        r"C:\path\to\your\videos"
    ]
    videos = []
    for path in search_paths:
        if os.path.exists(path):
            for file in os.listdir(path):
                if file.lower().endswith('.mp4'):
                    videos.append(os.path.join(path, file))
                    if len(videos) >= limit:
                        return videos
    return videos

class CapCutHeadless:
    def __init__(self):
        self.drafts_dir = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\User Data\Projects\com.lveditor.draft")
        self.template_dir = os.path.join(self.drafts_dir, "0506") # Empty template
        
    def execute_batch(self, project_name, video_paths):
        print(f"[{project_name}] 1. Initiating Headless Build...")
        
        target_dir = os.path.join(self.drafts_dir, project_name)
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        shutil.copytree(self.template_dir, target_dir)
        
        # Meta info
        meta_path = os.path.join(target_dir, "draft_meta_info.json")
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta['draft_name'] = project_name
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False)
            
        # Content info
        content_path = os.path.join(target_dir, "draft_content.json")
        with open(content_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            
        content['materials']['videos'] = []
        if not content['tracks']:
            content['tracks'] = [{"id": str(uuid.uuid4()), "type": "video", "segments": []}]
        video_track = next((t for t in content['tracks'] if t['type'] == 'video'), content['tracks'][0])
        video_track['segments'] = []
        
        current_time = 0
        resolutions = set()
        total_duration = 0
        valid_clips = 0
        
        for v_path in video_paths:
            info = get_video_info(v_path)
            if not info: continue
            
            valid_clips += 1
            mat_id = str(uuid.uuid4())
            seg_id = str(uuid.uuid4())
            dur = info['duration_micros']
            resolutions.add(f"{info['width']}x{info['height']}")
            
            # Inject Material
            content['materials']['videos'].append({
                "id": mat_id,
                "path": info['path'],
                "duration": dur,
                "type": "video",
                "width": info['width'],
                "height": info['height']
            })
            
            # Inject Timeline Segment (Seamless)
            video_track['segments'].append({
                "id": seg_id,
                "material_id": mat_id,
                "source_timerange": {"start": 0, "duration": dur},
                "target_timerange": {"start": current_time, "duration": dur}
            })
            
            current_time += dur
            total_duration += dur
            
        # Modify overall duration
        content['duration'] = total_duration
        
        with open(content_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, ensure_ascii=False)
            
        print(f"[{project_name}] 2. Build Complete. Generating Report...")
        print("="*50)
        print("--- EXECUTION LOG (Batch 01) ---")
        print("="*50)
        print(f"[+] Videos Injected : {valid_clips}")
        print(f"[+] Total Duration  : {total_duration / 1000000:.2f} Seconds")
        print(f"[+] Resolutions Found: {', '.join(resolutions)}")
        if len(resolutions) > 1:
            print("[!] WARNING: Resolution mismatch detected! The project contains mixed aspect ratios.")
        else:
            print("[V] RESOLUTION CHECK: Perfect match across all clips.")
        print("="*50)
        
        print(f"[{project_name}] 3. Terminating active CapCut instances...")
        subprocess.run(["taskkill", "/F", "/IM", "CapCut.exe"], capture_output=True)
        
        print(f"[{project_name}] 4. Launching CapCut directly to the project...")
        capcut_exe = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\Apps\CapCut.exe")
        project_file = os.path.join(target_dir, "draft_meta_info.json") # Capcut can be launched with project meta
        # Actually CapCut command line just needs the folder or no args then we open it from home
        # For true direct launch:
        subprocess.Popen([capcut_exe, project_file])

if __name__ == "__main__":
    engine = CapCutHeadless()
    videos = find_videos(limit=3)
    if not videos:
        print("[!] No videos found in the specified directories. Creating a dummy file to test.")
        # Create dummy video if nothing found
        dummy = r"D:\ط§ظ„ظ…ط´ط§ط±ظٹط¹\ظƒط§ط¨ ظƒط§طھ\dummy.mp4"
        import numpy as np
        out = cv2.VideoWriter(dummy, cv2.VideoWriter_fourcc(*'mp4v'), 30, (1920, 1080))
        for _ in range(60): out.write(np.zeros((1080, 1920, 3), dtype=np.uint8))
        out.release()
        videos = [dummy]
        
    engine.execute_batch("Headless_01", videos)

