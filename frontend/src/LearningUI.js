import React, { useState, useRef, useEffect } from "react";

export default function LearningUI() {
  const [text, setText] = useState("");
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
      <div className="relative text-center p-6 rounded-lg shadow-lg bg-[#B4BFD2]/70 backdrop-blur-sm flex flex-col items-center w-full max-w-3xl z-10">
        <h1 className="text-3xl font-nunito font-bold text-[#051B3D] mb-6">
          What would you like to learn today?
        </h1>

        {/* Textarea with upload button */}
        <div className="relative w-full max-w-2xl mb-4">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Type your query..."
            className="w-full px-4 py-3 pr-12 rounded-lg border border-[#528E78] focus:outline-none focus:ring-2 focus:ring-[#051B3D] resize-none overflow-hidden text-lg"
            style={{ minHeight: "3rem" }}
          />
          <button className="absolute right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 flex items-center justify-center rounded-full bg-[#051B3D] text-white hover:bg-[#528E78]">
            +
          </button>
        </div>

        {/* Buttons + dropdowns row */}
        <div className="flex flex-wrap items-center gap-4">
          {/* Complexity dropdown */}
          <div className="flex flex-col">
            <label className="text-sm font-nunito font-bold text-[#051B3D] mb-1">Complexity</label>
            <select className="rounded-lg border border-[#528E78] px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[#051B3D]">
              <option>Beginner</option>
              <option>Intermediate</option>
              <option>Advanced</option>
            </select>
          </div>

          {/* Depth dropdown */}
          <div className="flex flex-col">
            <label className="text-sm font-nunito font-bold text-[#051B3D] mb-1">Depth</label>
            <select className="rounded-lg border border-[#528E78] px-2 py-1 focus:outline-none focus:ring-2 focus:ring-[#051B3D]">
              <option>Overview</option>
              <option>Detailed</option>
              <option>Comprehensive</option>
            </select>
          </div>

          {/* Go button */}
          <button className="w-32 py-2 rounded-lg bg-[#051B3D] text-white font-semibold hover:bg-[#528E78] transition-colors">
            Go
          </button>
        </div>
      </div>
    </div>
  );
}
