import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import LineChart from "../components/LineChart.jsx";
import { latest, series } from "../api.js";

function isoFromNow(hours) {
  return new Date(Date.now() - hours * 3600 * 1000).toISOString();
}

const norm = (arr) =>
  (arr || [])
    .filter((p) => p && p.ts && p.value !== null && p.value !== undefined)
    .map((p) => ({ ts: p.ts, value: Number(p.value) }));

export default function Device() {
  const tenant = "demo";
  const { deviceId } = useParams();

  const [rangeH, setRangeH] = useState(24);
  const [lat, setLat] = useState(null);

  const [tempPts, setTempPts] = useState([]);
  const [v12Pts, setV12Pts] = useState([]);
  const [v5Pts, setV5Pts] = useState([]);

  const [err, setErr] = useState(null);

  async function loadAll() {
    try {
      setErr(null);

      const l = await latest(tenant, deviceId);
      setLat(l);

      const from_ts = isoFromNow(rangeH);

      const t = norm(await series(tenant, deviceId, "temp_c", { from_ts, limit: 2000 }));
      const s12 = norm(await series(tenant, deviceId, "psu_12v", { from_ts, limit: 2000 }));
      const s5 = norm(await series(tenant, deviceId, "psu_5v", { from_ts, limit: 2000 }));

      setTempPts(t);
      setV12Pts(s12);
      setV5Pts(s5);

      // debug (opcional)
      // console.log("tempPts sample", t.slice(0, 3));
    } catch (e) {
      setErr(String(e));
    }
  }

  useEffect(() => {
    loadAll();
    const t = setInterval(loadAll, 5000);
    return () => clearInterval(t);
  }, [deviceId, rangeH]);

  return (
    <div>
      <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12 }}>
        <h2 style={{ margin: "8px 0 12px", fontSize: 18 }}>Device: {deviceId}</h2>

        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <span style={{ opacity: 0.7, fontSize: 13 }}>Range</span>
          {[1, 6, 24, 168].map((h) => (
            <button
              key={h}
              onClick={() => setRangeH(h)}
              style={{
                padding: "6px 10px",
                borderRadius: 8,
                border: "1px solid #ddd",
                background: rangeH === h ? "#f0f0f0" : "white",
                cursor: "pointer",
              }}
            >
              {h === 168 ? "7d" : `${h}h`}
            </button>
          ))}
        </div>
      </div>

      {err && <pre style={{ color: "crimson", whiteSpace: "pre-wrap" }}>{err}</pre>}

      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <div style={{ opacity: 0.7, fontSize: 12 }}>temp_c</div>
          <div style={{ fontSize: 22 }}>{lat?.metrics?.temp_c ?? "—"}</div>
        </div>
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <div style={{ opacity: 0.7, fontSize: 12 }}>psu_12v</div>
          <div style={{ fontSize: 22 }}>{lat?.metrics?.psu_12v ?? "—"}</div>
        </div>
        <div style={{ border: "1px solid #eee", borderRadius: 12, padding: 12 }}>
          <div style={{ opacity: 0.7, fontSize: 12 }}>psu_5v</div>
          <div style={{ fontSize: 22 }}>{lat?.metrics?.psu_5v ?? "—"}</div>
        </div>
      </div>

      <div style={{ marginTop: 16, display: "grid", gridTemplateColumns: "1fr", gap: 12 }}>
        <LineChart title="Temperature (temp_c)" datasets={[{ label: "temp_c", points: tempPts }]} />
        <LineChart
          title="Power rails (12V / 5V)"
          datasets={[
            { label: "psu_12v", points: v12Pts },
            { label: "psu_5v", points: v5Pts },
          ]}
        />
      </div>
    </div>
  );
}
