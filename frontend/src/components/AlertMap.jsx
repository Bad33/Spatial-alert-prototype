// frontend/src/components/AlertMap.jsx
import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
} from "react-leaflet";
import axios from "axios";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

/* ---------- patch default marker icons (needed when using Vite) ---------- */
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL(
    "leaflet/dist/images/marker-icon-2x.png",
    import.meta.url
  ).href,
  iconUrl: new URL("leaflet/dist/images/marker-icon.png", import.meta.url).href,
  shadowUrl: new URL(
    "leaflet/dist/images/marker-shadow.png",
    import.meta.url
  ).href,
});

export default function AlertMap() {
  /* -------------- state -------------- */
  const [alertList, setAlertList] = useState([]);
  const [clusters, setClusters] = useState([]);

  /* -------------- side-effects -------------- */
  useEffect(() => {
    /* get latest alerts */
    axios
      .get("http://127.0.0.1:8000/alerts?limit=500")
      .then((r) => setAlertList(r.data ?? []))
      .catch(console.error);

    /* get hotspot centroids */
    axios
      .get("http://127.0.0.1:8000/clusters?eps_km=3&min_samples=10")
      .then((r) => setClusters(r.data?.features ?? []))
      .catch(console.error);
  }, []);

  /* -------------- render -------------- */
  return (
    <MapContainer
      center={[41.88, -87.62]} /* Chicago-ish dummy center */
      zoom={10}
      style={{ height: "100vh", width: "100%" }}
      scrollWheelZoom
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      {/* red dots = individual alerts */}
      {alertList.map((a) => (
        <CircleMarker
          key={a.alert_id}
          center={[a.latitude, a.longitude]}
          radius={4}
          pathOptions={{ color: "red" }}
        >
          <Popup>
            <strong>{a.alert_type}</strong>
            <br />
            {a.timestamp}
            <br />
            Severity: {a.severity ?? "?"}
          </Popup>
        </CircleMarker>
      ))}

      {/* blue circles = DBSCAN hotspot centroids */}
      {clusters.map((f) => (
        <CircleMarker
          key={f.properties.cluster_id}
          center={[f.geometry.coordinates[1], f.geometry.coordinates[0]]}
          radius={10}
          pathOptions={{ color: "blue" }}
        >
          <Popup>
            Hotspot #{f.properties.cluster_id}
            <br />
            Alerts: {f.properties.count}
          </Popup>
        </CircleMarker>
      ))}
    </MapContainer>
  );
}
