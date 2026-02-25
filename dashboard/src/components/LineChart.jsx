import React, { useEffect, useRef } from "react";
import { Chart } from "chart.js/auto";

/**
 * datasets: [{ label: string, points: [{ts, value}] }]
 */
export default function LineChart({ title, datasets, height = 280 }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    // create once
    chartRef.current = new Chart(canvasRef.current, {
      type: "line",
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { x: { ticks: { maxTicksLimit: 8 } } },
        interaction: { mode: "index", intersect: false },
        plugins: { legend: { display: true } },
        elements: { point: { radius: 0 } },
      },
    });

    return () => {
      chartRef.current?.destroy();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!chartRef.current) return;

    // Build a unified x-axis based on first dataset timestamps (MVP)
    const base = datasets?.[0]?.points ?? [];
    const labels = base.map((p) => new Date(p.ts).toLocaleString());

    chartRef.current.data.labels = labels;
    chartRef.current.data.datasets = (datasets || []).map((ds) => ({
      label: ds.label,
      data: (ds.points || []).map((p) => p.value),
      tension: 0.15,
    }));

    chartRef.current.update();
  }, [datasets]);

  return (
    <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
      <div style={{ marginBottom: 8, fontWeight: 600 }}>{title}</div>
      <div style={{ height }}>
        <canvas ref={canvasRef}></canvas>
      </div>
    </div>
  );
}
