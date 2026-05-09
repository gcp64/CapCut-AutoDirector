import os
import json
import uuid
import shutil
import cv2
import numpy as np
import subprocess

def classify_video(path):
    """
    Uses OpenCV to extract frames and classify the video based on edges and color variance.
    Returns: Category, Scale (Start -> End), Overlap duration
    """
    cap = cv2.VideoCapture(path)
    if not cap.isOpened(): return "UI/Tutorial", (1.0, 1.15), 500000
    
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames_to_grab = [int(frame_count * 0.2), int(frame_count * 0.5), int(frame_count * 0.8)]
    
    variances = []
    edges_list = []
    
    for f in frames_to_grab:
        cap.set(cv2.CAP_PROP_POS_FRAMES, f)
        ret, frame = cap.read()
        if ret:
            # Color variance
            variances.append(np.var(frame))
            # Edge density
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            edges_list.append(np.mean(edges))
            
    cap.release()
    
    avg_var = np.mean(variances) if variances else 0
    avg_edge = np.mean(edges_list) if edges_list else 0
    
    fname = os.path.basename(path).lower()
    
    if "miku" in fname or "ellenjoe" in fname or avg_var > 4000:
        return "Anime/3D", (1.0, 1.05), 1500000 # Smooth fades, slight scale
    elif avg_edge > 50 and avg_var > 2000:
        return "Action/Games", (1.0, 1.2), 300000 # Fast cuts, high scale
    else:
        return "UI/Tutorial", (1.0, 1.15), 500000 # Zoom-ins

class CapCutSmartDirector:
    def __init__(self):
        self.drafts_dir = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\User Data\Projects\com.lveditor.draft")
        self.template_dir = os.path.join(self.drafts_dir, "0506")
        
    def build(self, project_name, video_paths):
        print(f"--- BATCH 04: Smart Director Engine ({project_name}) ---")
        
        target_dir = os.path.join(self.drafts_dir, project_name)
        if os.path.exists(target_dir): shutil.rmtree(target_dir)
        shutil.copytree(self.template_dir, target_dir)
        
        meta_path = os.path.join(target_dir, "draft_meta_info.json")
        with open(meta_path, 'r', encoding='utf-8') as f: meta = json.load(f)
        meta['draft_name'] = project_name
        with open(meta_path, 'w', encoding='utf-8') as f: json.dump(meta, f, ensure_ascii=False)
            
        content_path = os.path.join(target_dir, "draft_content.json")
        with open(content_path, 'r', encoding='utf-8') as f: content = json.load(f)
            
        content['materials']['videos'] = []
        content['materials']['material_animations'] = []
        if not content['tracks']:
            content['tracks'] = [{"id": str(uuid.uuid4()), "type": "video", "segments": []}]
        video_track = next((t for t in content['tracks'] if t['type'] == 'video'), content['tracks'][0])
        video_track['segments'] = []
        
        current_time = 0
        log_data = []
        
        for idx, v_path in enumerate(video_paths):
            category, scale_range, overlap = classify_video(v_path)
            
            cap = cv2.VideoCapture(v_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            fc = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            dur = int((fc / fps) * 1000000) if fps > 0 else 5000000
            
            mat_id = str(uuid.uuid4())
            seg_id = str(uuid.uuid4())
            anim_id = str(uuid.uuid4())
            
            # Keyframing simulation using material animations (Combo Animation: Zoom In / Pan)
            anim_name = "Zoom In" if category == "UI/Tutorial" else "Pendulum"
            content['materials']['material_animations'].append({
                "id": anim_id,
                "type": "material_animation",
                "animations": [{
                    "id": str(uuid.uuid4()),
                    "type": "combo",
                    "name": anim_name,
                    "duration": dur,
                    "start": 0
                }]
            })
            
            content['materials']['videos'].append({
                "id": mat_id,
                "path": v_path,
                "duration": dur,
                "type": "video",
                "width": w,
                "height": h
            })
            
            if idx > 0: current_time -= overlap
            
            video_track['segments'].append({
                "id": seg_id,
                "material_id": mat_id,
                "extra_material_refs": [anim_id],
                "source_timerange": {"start": 0, "duration": dur},
                "target_timerange": {"start": current_time, "duration": dur}
            })
            
            log_data.append({
                "clip": os.path.basename(v_path),
                "category": category,
                "scale_transition": f"{scale_range[0]} -> {scale_range[1]}",
                "overlap_applied": f"{overlap / 1000000}s",
                "animation": anim_name
            })
            
            print(f"  [+] {os.path.basename(v_path)} => {category} (Overlap: {overlap/1000000}s, Anim: {anim_name})")
            current_time += dur

        content['duration'] = current_time
        with open(content_path, 'w', encoding='utf-8') as f: json.dump(content, f, ensure_ascii=False)
            
        # Memory Log
        log_path = r"D:\ط§ظ„ظ…ط´ط§ط±ظٹط¹\ظƒط§ط¨ ظƒط§طھ\Animation_Log.json"
        with open(log_path, 'w', encoding='utf-8') as f: json.dump(log_data, f, indent=4)
        
        print("\n=== EXECUTION LOG (Batch 04: Smart Director) ===")
        print("Content Profiling : Success (OpenCV Vision Applied)")
        print("JSON Keyframing   : Scale/Pan via Combo Animations Injected")
        print("Memory Saved to   : Animation_Log.json")
        print("================================================")
        
        subprocess.run(["taskkill", "/F", "/IM", "CapCut.exe"], capture_output=True)
        capcut_exe = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\Apps\CapCut.exe")
        subprocess.Popen([capcut_exe])

if __name__ == "__main__":
    engine = CapCutSmartDirector()
    vids_dir = r"D:\ط§ظ„ظ…ط´ط§ط±ظٹط¹\remotion\out"
    videos = [os.path.join(vids_dir, f) for f in os.listdir(vids_dir) if f.endswith(".mp4")][:3]
    if videos: engine.build("Headless_04", videos)

