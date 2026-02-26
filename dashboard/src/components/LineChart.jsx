import React, { useEffect, useRef } from "react";
import { Chart } from "chart.js/auto";

function tsKey(ts) {
  return String(ts);
}

/**
 * datasets: [{ label: string, points: [{ts, value}] }]
 * Unifies timestamps across datasets and aligns values by timestamp.
 */
export default function LineChart({ title, datasets, height = 280 }) {
  const canvasRef = useRef(null);
  const chartRef = useRef(null);

  useEffect(() => {
    chartRef.current = new Chart(canvasRef.current, {
      type: "line",
      data: { labels: [], datasets: [] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: { mode: "index", intersect: false },
        plugins: { legend: { display: true } },
        elements: { point: { radius: 0 } },
        scales: { x: { ticks: { maxTicksLimit: 8 } } },
      },
    });

    return () => {
      chartRef.current?.destroy();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!chartRef.current) return;

    const dss = datasets || [];

    // 1) collect all timestamps across all datasets
    const tsSet = new Set();
    for (const ds of dss) {
      for (const p of (ds.points || [])) {
        if (p?.ts) tsSet.add(tsKey(p.ts));
      }
    }

    // If no points, clear chart
    if (tsSet.size === 0) {
      chartRef.current.data.labels = [];
      chartRef.current.data.datasets = [];
      chartRef.current.update();
      return;
    }

    // 2) sorted timestamps (ISO strings sort OK)
    const tsList = Array.from(tsSet).sort();
    const labels = tsList.map((ts) => new Date(ts).toLocaleString());

    // 3) build aligned series (missing points -> null)
    const chartDatasets = dss.map((ds) => {
      const m = new Map();
      for (const p of (ds.points || [])) {
        if (p?.ts) m.set(tsKey(p.ts), p.value);
      }
      const data = tsList.map((ts) => {
        const v = m.get(ts);
        return v === undefined || v === null ? null : Number(v);
      });
      return { label: ds.label, data, tension: 0.15 };
    });

    chartRef.current.data.labels = labels;
    chartRef.current.data.datasets = chartDatasets;
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
