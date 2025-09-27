import shutil
import os
import subprocess

def render_video(results_json):
    # Step 1. clean up generated code
    shutil.rmtree("generated", ignore_errors=True)
    os.mkdir("generated")

    # Step 2. generate code
    for file in results_json['sceneFiles']:
        filename = file['filename']
        with open("generated/" + filename, "w", encoding="utf-8") as f:
            f.write(file['code'])

    with open("generated/" + results_json['masterFile']['filename'], "w", encoding="utf-8") as f:
        f.write(results_json['masterFile']['content'])

    # Step 3: render each scene
    os.chdir("generated")
    scenes = [
        ("master_animation.py", "MasterExplainerScene"),
    ]

    for file in results_json['sceneFiles']:
        scenes.append((file['filename'], file['className']))

    videos = []

    for fname, scene in scenes:
        try:
            subprocess.run(["manim", "-qm", fname, scene], check=True)
            print(f"Rendered {fname}")
            videos.append(f"./media/videos/{fname.replace('.py', '')}/720p30/{scene}.mp4")
        except Exception as e:
            print(f"Error rendering {fname}: {e}")
    
    # Step 4: combine videos
    # Write the list of video files to a text file for ffmpeg concat
    with open("videos_to_concat.txt", "w", encoding="utf-8") as f:
        for video in videos:
            f.write(f"file '{video}'\n")

    # Use ffmpeg with -f concat to combine the videos
    subprocess.run([
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "videos_to_concat.txt",
        "-c", "copy",
        "combined.mp4"
    ])

    # Step 5: copy the combined video to the root directory
    shutil.copy("combined.mp4", "../combined.mp4")
    

if __name__ == "__main__":
    import json

    results_json = json.load(open("result.json", "r", encoding="utf-8"))

    render_video(results_json)