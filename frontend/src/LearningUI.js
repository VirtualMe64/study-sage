import React, { useState, useRef, useEffect } from "react";
import ApiService from "./services/api";

export default function LearningUI() {
  const [text, setText] = useState("");
  const [complexity, setComplexity] = useState("intermediate");
  const [depth, setDepth] = useState("detailed");
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const textareaRef = useRef(null);
  const canvasRef = useRef(null);

  // Auto-expand text area
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = textarea.scrollHeight + "px";
    }
  }, [text]);

  // Poll job status if we have an active job
  useEffect(() => {
    if (!jobId || !isLoading) return;

    const pollInterval = setInterval(async () => {
      try {
        const status = await ApiService.getJobStatus(jobId);
        setJobStatus(status);

        if (status.status === "completed") {
          setIsLoading(false);
          setResult(status.result);
          setJobId(null);
          clearInterval(pollInterval);
        } else if (status.status === "error") {
          setIsLoading(false);
          setError(status.error);
          setJobId(null);
          clearInterval(pollInterval);
        }
      } catch (err) {
        console.error("Error polling job status:", err);
        clearInterval(pollInterval);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [jobId, isLoading]);

  // Dynamic drifting + rotating network background
  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    let animationFrameId;

    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();

    const nodes = Array.from({ length: 50 }, () => ({
      x: Math.random() * (canvas.width * 1.5) - canvas.width * 0.25,
      y: Math.random() * (canvas.height * 1.5) - canvas.height * 0.25,
      r: 2 + Math.random() * 2,
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.25,
    }));

    const maxDist = 250;
    let angle = 0;

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.save();
      ctx.translate(canvas.width / 2, canvas.height / 2);
      ctx.rotate(angle);
      ctx.translate(-canvas.width / 2, -canvas.height / 2);

      nodes.forEach((n) => {
        n.x += n.vx;
        n.y += n.vy;
        if (n.x < -canvas.width * 0.25 || n.x > canvas.width * 1.25) n.vx *= -1;
        if (n.y < -canvas.height * 0.25 || n.y > canvas.height * 1.25) n.vy *= -1;
      });

      nodes.forEach((a, i) => {
        nodes.forEach((b, j) => {
          if (i !== j) {
            const dist = Math.hypot(a.x - b.x, a.y - b.y);
            if (dist < maxDist) {
              const opacity = 1 - dist / maxDist;
              ctx.strokeStyle = `rgba(200, 220, 255, ${0.2 * opacity})`;
              ctx.lineWidth = 1;
              ctx.beginPath();
              ctx.moveTo(a.x, a.y);
              ctx.lineTo(b.x, b.y);
              ctx.stroke();
            }
          }
        });
      });

      nodes.forEach((n) => {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(220, 235, 255, 0.8)";
        ctx.fill();
      });

      ctx.restore();
      angle += 0.0003 * Math.PI * 2;
    };

    const animate = () => {
      draw();
      animationFrameId = requestAnimationFrame(animate);
    };
    animate();

    window.addEventListener("resize", resizeCanvas);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", resizeCanvas);
    };
  }, []);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!text.trim()) {
      setError("Please enter a topic to learn about");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setJobId(null);
    setJobStatus(null);

    try {
      const response = await ApiService.generateLesson({
        topic: text.trim(),
        complexity,
        depth,
        style: "clean and modern"
      });

      if (response.success) {
        setJobId(response.job_id);
        // Job status will be polled by useEffect
      } else {
        setError(response.message || "Failed to generate content");
        setIsLoading(false);
      }
    } catch (err) {
      setError(err.message || "An error occurred while processing your request");
      setIsLoading(false);
    }
  };

  // Handle step-by-step generation
  const handleStepByStep = async (phase) => {
    if (!text.trim()) {
      setError("Please enter a topic to learn about");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      let response;
      
      if (phase === 1) {
        response = await ApiService.generatePhase1({
          topic: text.trim(),
          complexity,
          depth,
          style: "clean and modern"
        });
      } else if (phase === 2 && result && result.phase3_data) {
        response = await ApiService.generatePhase2(result.phase3_data);
      } else if (phase === 3 && result && result.phase3_data) {
        response = await ApiService.generatePhase3(result.phase3_data);
      } else {
        throw new Error("Invalid phase or missing data");
      }

      if (response.success) {
        setResult(prev => ({
          ...prev,
          [`phase${phase}_data`]: response.data
        }));
      } else {
        setError(response.message || "Failed to generate content");
      }
    } catch (err) {
      setError(err.message || "An error occurred while processing your request");
    } finally {
      setIsLoading(false);
    }
  };

  // Render videos
  const handleRenderVideos = async () => {
    if (!result || !result.phase3_data) {
      setError("No Phase 3 data available for rendering");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await ApiService.renderVideos(result.phase3_data);
      
      if (response.success) {
        setJobId(response.job_id);
        // Job status will be polled by useEffect
      } else {
        setError(response.message || "Failed to start video rendering");
        setIsLoading(false);
      }
    } catch (err) {
      setError(err.message || "An error occurred while rendering videos");
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen flex items-start justify-center bg-gradient-to-br from-[#010A17] to-[#28497C] pt-60 pb-24 overflow-hidden">
      {/* Background Canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0 w-full h-full"
        style={{ zIndex: 0 }}
      />

      {/* Grain overlay */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E\")",
          opacity: 0.07,
          zIndex: 1,
        }}
      />

      {/* Logo + Text */}
      <div className="absolute top-2 left-2 flex items-center z-20">
        <img
          src="/logo512.png"
          alt="Logo"
          className="w-[96px] h-[144px]"
        />
        <div
          className="ml-2 font-nunito font-bold text-[#F8F8F2]"
          style={{
            fontSize: "36px",
            lineHeight: "72px",
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
          }}
        >
          <span style={{ lineHeight: "1" }}>Study</span>
          <span style={{ lineHeight: "1" }}>Sage</span>
        </div>
      </div>

      {/* Foreground UI */}
      <div className="relative text-center p-6 rounded-lg shadow-lg bg-[#B4BFD2]/70 backdrop-blur-sm flex flex-col items-center w-full max-w-4xl z-10">
        <h1 className="text-3xl font-nunito font-bold text-[#051B3D] mb-6">
          What would you like to learn today?
        </h1>

        <form onSubmit={handleSubmit} className="w-full">
          {/* Textarea with upload button */}
          <div className="relative w-full max-w-2xl mb-4">
            <textarea
              ref={textareaRef}
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type your query..."
              className="w-full px-4 py-3 pr-12 rounded-lg border border-[#528E78] focus:outline-none focus:ring-2 focus:ring-[#051B3D] resize-none overflow-hidden text-lg"
              style={{ minHeight: "3rem" }}
              disabled={isLoading}
            />
            <button 
              type="button"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-full bg-[#051B3D] text-white hover:bg-[#528E78]"
            >
              +
            </button>
          </div>

          {/* Buttons + dropdowns row */}
          <div className="flex flex-wrap items-center gap-4">
            {/* Complexity dropdown */}
            <div className="flex flex-col">
              <label className="text-sm font-nunito font-bold text-[#051B3D] mb-1">Complexity</label>
              <select 
                value={complexity}
                onChange={(e) => setComplexity(e.target.value)}
                className="rounded-lg border border-[#528E78] px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[#051B3D]"
                disabled={isLoading}
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            {/* Depth dropdown */}
            <div className="flex flex-col">
              <label className="text-sm font-nunito font-bold text-[#051B3D] mb-1">Depth</label>
              <select 
                value={depth}
                onChange={(e) => setDepth(e.target.value)}
                className="rounded-lg border border-[#528E78] px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[#051B3D]"
                disabled={isLoading}
              >
                <option value="overview">Overview</option>
                <option value="detailed">Detailed</option>
                <option value="comprehensive">Comprehensive</option>
              </select>
            </div>

            {/* Generate button */}
            <button 
              type="submit"
              disabled={isLoading}
              className="w-32 py-2 rounded-lg bg-[#051B3D] text-white font-semibold hover:bg-[#528E78] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Generating..." : "Generate"}
            </button>
          </div>
        </form>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="mt-4 p-4 bg-blue-100 border border-blue-400 text-blue-700 rounded-lg">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-700 mr-2"></div>
              {jobStatus ? (
                <div>
                  <div>Phase: {jobStatus.phase}</div>
                  <div>Progress: {jobStatus.progress}%</div>
                </div>
              ) : (
                "Generating your educational content..."
              )}
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="mt-6 w-full text-left">
            <h2 className="text-2xl font-nunito font-bold text-[#051B3D] mb-4">
              Generated Content
            </h2>
            
            {/* Phase 1 Results */}
            {result.phase1_data && (
              <div className="mb-6 p-4 bg-white/80 rounded-lg">
                <h3 className="text-xl font-semibold text-[#051B3D] mb-2">
                  Phase 1: Scene Mapping
                </h3>
                <div className="text-sm text-gray-600 mb-2">
                  {result.phase1_data.scenes?.length || 0} scenes generated
                </div>
                <button
                  onClick={() => handleStepByStep(2)}
                  className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                >
                  Generate Phase 2 (Detailed Scripts)
                </button>
              </div>
            )}

            {/* Phase 2 Results */}
            {result.phase2_data && (
              <div className="mb-6 p-4 bg-white/80 rounded-lg">
                <h3 className="text-xl font-semibold text-[#051B3D] mb-2">
                  Phase 2: Detailed Scripts
                </h3>
                <div className="text-sm text-gray-600 mb-2">
                  Scripts generated for {result.phase2_data.scenes?.length || 0} scenes
                </div>
                <button
                  onClick={() => handleStepByStep(3)}
                  className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                >
                  Generate Phase 3 (Manim Code)
                </button>
              </div>
            )}

            {/* Phase 3 Results */}
            {result.phase3_data && (
              <div className="mb-6 p-4 bg-white/80 rounded-lg">
                <h3 className="text-xl font-semibold text-[#051B3D] mb-2">
                  Phase 3: Manim Code Generation
                </h3>
                <div className="text-sm text-gray-600 mb-2">
                  {result.phase3_data.sceneFiles?.length || 0} scene files generated
                </div>
                <button
                  onClick={handleRenderVideos}
                  className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
                >
                  Render Videos
                </button>
              </div>
            )}

            {/* Lesson Plan */}
            {result.phase3_data?.lessonPlan && (
              <div className="mb-6 p-4 bg-white/80 rounded-lg">
                <h3 className="text-xl font-semibold text-[#051B3D] mb-2">
                  {result.phase3_data.lessonPlan.title}
                </h3>
                <h4 className="text-lg font-medium text-[#051B3D] mb-2">Learning Objectives:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {result.phase3_data.lessonPlan.objectives.map((objective, index) => (
                    <li key={index} className="text-[#051B3D]">{objective}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Scene Files */}
            {result.phase3_data?.sceneFiles && result.phase3_data.sceneFiles.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-[#051B3D] mb-4">
                  Generated Manim Scenes ({result.phase3_data.totalScenes})
                </h3>
                <div className="space-y-4">
                  {result.phase3_data.sceneFiles.map((scene, index) => (
                    <div key={scene.id} className="p-4 bg-white/80 rounded-lg">
                      <h4 className="text-lg font-medium text-[#051B3D] mb-2">
                        Scene {index + 1}: {scene.className}
                      </h4>
                      <div className="bg-gray-100 p-3 rounded text-sm font-mono overflow-x-auto max-h-40">
                        <pre>{scene.code}</pre>
                      </div>
                      {scene.validationResults && (
                        <div className="mt-2 text-sm">
                          <span className={`px-2 py-1 rounded ${
                            scene.validationResults.syntaxValid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {scene.validationResults.syntaxValid ? '✓ Valid' : '✗ Invalid'}
                          </span>
                          {scene.validationResults.warnings?.length > 0 && (
                            <div className="mt-1 text-yellow-700">
                              Warnings: {scene.validationResults.warnings.join(', ')}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Video Results */}
            {result.videos && (
              <div className="p-4 bg-white/80 rounded-lg">
                <h3 className="text-lg font-semibold text-[#051B3D] mb-2">
                  Generated Videos
                </h3>
                <div className="text-sm text-gray-600 mb-2">
                  {result.video_count} videos rendered
                </div>
                {result.complete_video && (
                  <div className="mt-2">
                    <a 
                      href={ApiService.getFileUrl(result.complete_video.split('/').pop())}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      Download Complete Video
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
