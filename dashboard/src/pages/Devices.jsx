import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { listDevices } from "../api.js";
import { ageSeconds, deviceState, fmtAge } from "../lib/status";

export default function Devices() {
  const tenant = "demo";
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState(null);

  useEffect(() => {
    let alive = true;
    async function load() {
      try {
        const data = await listDevices(tenant);
        if (alive) setRows(data);
      } catch (e) {
        if (alive) setErr(String(e));
      }
    }
    load();
    const t = setInterval(load, 5000);
    return () => { alive = false; clearInterval(t); };
  }, []);

  const table = useMemo(() => {
    return rows.map(r => ({
      ...r,
      age_s: ageSeconds(r.last_seen_at),
    })).sort((a, b) => (a.device_id > b.device_id ? 1 : -1));
  }, [rows]);

  if (err) {
    return <pre style={{ color: "crimson", whiteSpace: "pre-wrap" }}>{err}</pre>;
  }

  return (
    <div>
      <div
    	style={{
	      display: "flex",
	      justifyContent: "space-between",
	      alignItems: "baseline",
	      margin: "8px 0 12px",
	    }}
	  >
	    <h2 style={{ margin: 0, fontSize: 18 }}>Devices</h2>

	    <span style={{ fontSize: 12, opacity: 0.6 }}>
	      auto refresh: 5s
          </span>
       </div>
      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
              <th style={{ padding: 8 }}>Device</th>
	      <th style={{ padding: 8 }}>Status</th>
              <th style={{ padding: 8 }}>Last seen</th>
              <th style={{ padding: 8 }}>Age</th>
            </tr>
          </thead>
	  <tbody>
	  {table.map((r) => {
	    const st = deviceState(r.age_s);
	    return (
	      <tr key={r.device_id} style={{ borderBottom: "1px solid #f0f0f0" }}>
		<td style={{ padding: 8 }}>
		  <Link to={`/device/${encodeURIComponent(r.device_id)}`}>{r.device_id}</Link>
		</td>

		<td style={{ padding: 8 }}>
		  <span
		    style={{
		      background: st.color,
		      color: "white",
		      padding: "2px 8px",
		      borderRadius: 8,
		      fontSize: 12,
		      textTransform: "uppercase",
		    }}
		  >
		    {st.label}
		  </span>
		</td>

		<td style={{ padding: 8, fontFamily: "ui-monospace, monospace" }}>
		  {r.last_seen_at ?? "—"}
		</td>

		<td style={{ padding: 8 }}>{fmtAge(r.age_s)}</td>
	      </tr>
	    );
	  })}
	</tbody>
        </table>
      </div>
    </div>
  );
}


