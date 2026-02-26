import React from "react";
import { Link, Route, Routes } from "react-router-dom";
import Devices from "./pages/Devices.jsx";
import Device from "./pages/Device.jsx";

export default function App() {
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", maxWidth: 1100, margin: "0 auto", padding: 16 }}>
      <header style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 12 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 22 }}>RF Site Telemetry — Demo</h1>
          <div style={{ opacity: 0.7, fontSize: 13 }}>Public read-only tenant: demo</div>
        </div>
        <nav style={{ display: "flex", gap: 12 }}>
          <Link to="/" style={{ textDecoration: "none" }}>Devices</Link>
        </nav>
      </header>

      <hr style={{ margin: "16px 0" }} />

      <Routes>
        <Route path="/" element={<Devices />} />
        <Route path="/device/:deviceId" element={<Device />} />
      </Routes>

      <footer style={{ marginTop: 24, opacity: 0.6, fontSize: 12 }}>
        Powered by FastAPI + Postgres. API under <code>/api</code>.
      </footer>
    </div>
  );
}

