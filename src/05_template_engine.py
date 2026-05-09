import os
import json
import uuid
import shutil
import cv2
import subprocess

class CapCutTemplateEngine:
    def __init__(self):
        self.drafts_dir = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\User Data\Projects\com.lveditor.draft")
        self.template_dir = os.path.join(self.drafts_dir, "0506")
        self.db_path = r"D:\ط§ظ„ظ…ط´ط§ط±ظٹط¹\ظƒط§ط¨ ظƒط§طھ\CapCut_Templates_DB.json"
        
        with open(self.db_path, 'r', encoding='utf-8') as f:
            self.db = json.load(f)
            
    def apply_animation(self, content, seg_id, mat_id, anim_name):
        if anim_name not in self.db.get("animations", {}):
            print(f"  [WARN] Animation '{anim_name}' not found in DB.")
            return None
            
        anim_data = dict(self.db["animations"][anim_name])
        # Generate new UUIDs to prevent conflicts
        anim_data["id"] = str(uuid.uuid4())
        
        mat_anim_id = str(uuid.uuid4())
        
        # Inject into material_animations
        if 'material_animations' not in content['materials']:
            content['materials']['material_animations'] = []
            
        content['materials']['material_animations'].append({
            "id": mat_anim_id,
            "type": "material_animation",
            "animations": [anim_data]
        })
        
        return mat_anim_id
        
    def apply_text_template(self, content, text_name, start_time, duration):
        # Fallback to basic text if not found
        if text_name not in self.db.get("text_templates", {}):
            print(f"  [WARN] Text template '{text_name}' not found. Using Basic Text.")
            text_mat_id = str(uuid.uuid4())
            if 'texts' not in content['materials']: content['materials']['texts'] = []
            content['materials']['texts'].append({
                "id": text_mat_id,
                "type": "text",
                "content": f"<font id=\"\" path=\"\"><color><size>{text_name}</size></color></font>",
                "text_alpha": 1.0,
                "alignment": 1,
                "layer_weight": 1
            })
            mat_id = text_mat_id
        else:
            txt_data = dict(self.db["text_templates"][text_name])
            mat_id = str(uuid.uuid4())
            txt_data["id"] = mat_id
            content['materials']['text_templates'].append(txt_data)
            
        # Add to text track
        if not any(t.get('type') == 'text' for t in content['tracks']):
            content['tracks'].append({"id": str(uuid.uuid4()), "type": "text", "segments": []})
        text_track = next(t for t in content['tracks'] if t['type'] == 'text')
        
        seg_id = str(uuid.uuid4())
        text_track['segments'].append({
            "id": seg_id,
            "material_id": mat_id,
            "source_timerange": {"start": 0, "duration": duration},
            "target_timerange": {"start": start_time, "duration": duration}
        })
        print(f"  [+] Text Template '{text_name}' applied.")

    def build(self, project_name, video_path):
        print(f"--- BATCH 05: Template Injection Engine ({project_name}) ---")
        
        target_dir = os.path.join(self.drafts_dir, project_name)
        if os.path.exists(target_dir): shutil.rmtree(target_dir)
        shutil.copytree(self.template_dir, target_dir)
        
        meta_path = os.path.join(target_dir, "draft_meta_info.json")
        with open(meta_path, 'r', encoding='utf-8') as f: meta = json.load(f)
        meta['draft_name'] = project_name
        with open(meta_path, 'w', encoding='utf-8') as f: json.dump(meta, f, ensure_ascii=False)
            
        content_path = os.path.join(target_dir, "draft_content.json")
        with open(content_path, 'r', encoding='utf-8') as f: content = json.load(f)
            
        if 'videos' not in content['materials']: content['materials']['videos'] = []
        if not content['tracks']:
            content['tracks'] = [{"id": str(uuid.uuid4()), "type": "video", "segments": []}]
        video_track = next((t for t in content['tracks'] if t['type'] == 'video'), content['tracks'][0])
        
        # Add a single video
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        fc = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        dur = int((fc / fps) * 1000000) if fps > 0 else 5000000
        
        mat_id = str(uuid.uuid4())
        seg_id = str(uuid.uuid4())
        
        content['materials']['videos'].append({
            "id": mat_id, "path": video_path, "duration": dur, "type": "video", "width": w, "height": h
        })
        
        segment = {
            "id": seg_id,
            "material_id": mat_id,
            "source_timerange": {"start": 0, "duration": dur},
            "target_timerange": {"start": 0, "duration": dur},
            "extra_material_refs": []
        }
        
        # APPLY ANIMATION FROM DB
        anim_to_apply = "Zoom In" # Since this is the only one in DB right now
        anim_ref_id = self.apply_animation(content, seg_id, mat_id, anim_to_apply)
        if anim_ref_id:
            segment['extra_material_refs'].append(anim_ref_id)
            print(f"  [+] Animation '{anim_to_apply}' injected from DB.")
            
        video_track['segments'].append(segment)
        content['duration'] = dur
        
        # APPLY TEXT TEMPLATE FROM DB
        self.apply_text_template(content, "Cyberpunk Text", 0, 5000000)
        
        with open(content_path, 'w', encoding='utf-8') as f: json.dump(content, f, ensure_ascii=False)
            
        print("\n=== TEMPLATE ENGINE REPORT ===")
        print(f"Project built: {project_name}")
        print("Launching CapCut...")
        subprocess.run(["taskkill", "/F", "/IM", "CapCut.exe"], capture_output=True)
        capcut_exe = os.path.join(os.environ["LOCALAPPDATA"], r"CapCut\Apps\CapCut.exe")
        subprocess.Popen([capcut_exe])

if __name__ == "__main__":
    engine = CapCutTemplateEngine()
    video = r"D:\ط§ظ„ظ…ط´ط§ط±ظٹط¹\remotion\out\MasterSoulEdit.mp4"
    if os.path.exists(video):
        engine.build("Headless_Templates_01", video)
    else:
        print("Video not found.")

