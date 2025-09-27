import subprocess

scenes = [
    ("master_animation.py", "MasterExplainerScene"),
    ("visualizing_with_venn_diagrams.py", "VisualizingWithVennDiagrams"),
    ("logical_expressions_and_truth_tables.py", "LogicalExpressionsAndTruthTables"),
    ("conclusion_and_summary.py", "ConclusionAndSummary"), 
]

videos = []

for fname, scene in scenes:
    try:
        subprocess.run(["manim", "-qm", fname, scene], check=True)
        print(f"Rendered {fname}")
        videos.append(f"./media/videos/{fname.replace('.py', '')}/720p30/{scene}.mp4")
    except Exception as e:
        print(f"Error rendering {fname}: {e}")

# combine videos into one
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