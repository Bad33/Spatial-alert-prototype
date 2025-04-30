/*****************************************************************
  AlertMap.jsx  —  alerts pane z-index 750 + button moved right
*****************************************************************/
import { useEffect, useMemo, useState } from "react";
import {
  MapContainer,
  TileLayer,
  CircleMarker,
  Popup,
  Pane,                // NEW: we already imported but keep comment
  useMap,
} from "react-leaflet";
import axios from "axios";
import { io } from "socket.io-client";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.heat";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL("leaflet/dist/images/marker-icon-2x.png", import.meta.url).href,
  iconUrl:       new URL("leaflet/dist/images/marker-icon.png",    import.meta.url).href,
  shadowUrl:     new URL("leaflet/dist/images/marker-shadow.png", import.meta.url).href,
});

/* ---- tiny HeatLayer helper (no peer-dependency wrapper) ---- */
function HeatLayer({ points, max }) {
  const map = useMap();
  useEffect(() => {
    if (!points.length) return;
    const layer = L.heatLayer(points, {
      radius: 15,
      blur: 20,
      maxZoom: 17,
      max: max || Math.max(...points.map(p => p[2])),
    }).addTo(map);
    return () => map.removeLayer(layer);
  }, [points, max, map]);
  return null;
}

/* ---------------------- main component ---------------------- */
const socket = io("http://127.0.0.1:8000");

export default function AlertMap() {
  const [alertList, setAlertList] = useState([]);
  const [clusters, setClusters]   = useState([]);
  const [kdePoints, setKdePoints] = useState([]);
  const [layer, setLayer]         = useState("alerts");

  /* initial fetch ------------------------------------------------ */
  useEffect(() => {
    axios.get("http://127.0.0.1:8000/alerts?limit=500")
         .then(r => setAlertList(r.data ?? []));
    axios.get("http://127.0.0.1:8000/clusters?eps_km=3&min_samples=10")
         .then(r => setClusters(r.data?.features ?? []));
    axios.get("http://127.0.0.1:8000/kde?bw_km=1")
         .then(r => {
           const pts = r.data.lat.map((lat,i)=>[lat,r.data.lon[i],r.data.density[i]]);
           setKdePoints(pts);
         });
  }, []);

  /* live anomaly stream ----------------------------------------- */
  useEffect(() => {
    socket.on("anomaly", f => {
      const [lon,lat] = f.geometry.coordinates;
      setAlertList(p => [...p,{
        alert_id: f.properties.alert_id,
        latitude: lat, longitude: lon,
        alert_type: f.properties.alert_type,
        timestamp:  f.properties.timestamp,
        severity:  "Anomalous",
        _flash: true,
      }]);
    });
    return () => socket.off("anomaly");
  }, []);

  const heatMax = useMemo(
    () => (kdePoints.length ? Math.max(...kdePoints.map(p=>p[2])) : 0),
    [kdePoints]
  );

  /* ---------------------------- JSX --------------------------- */
  return (
    <>
      {/* toggle box — moved right (left: 60px) NEW */}
      <div style={{
        position:"absolute", top:10, left:60, zIndex:1000,
        background:"#fff", padding:"6px 8px", borderRadius:4,
        boxShadow:"0 1px 5px rgba(0,0,0,0.4)", fontSize:14,
      }}>
        <label><input type="radio" value="alerts" checked={layer==="alerts"}
               onChange={()=>setLayer("alerts")}/> Alerts</label>{" "}
        <label><input type="radio" value="heat"   checked={layer==="heat"}
               onChange={()=>setLayer("heat")}/> Heatmap</label>
      </div>

      <MapContainer
        center={[41.88,-87.62]} zoom={10} scrollWheelZoom
        style={{height:"100vh", width:"100%"}}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                   attribution="&copy; OpenStreetMap contributors" />

        {/* NEW pane for alerts — highest z-index */}
        <Pane name="alertPane" style={{ zIndex: 750 }} />

        {/* KDE heat */}
        {layer==="heat" && kdePoints.length>0 &&
          <HeatLayer points={kdePoints} max={heatMax}/>}

        {/* individual alerts in alertPane */}
        {layer==="alerts" && alertList.map(a=>(
          <CircleMarker key={a.alert_id}
            center={[a.latitude,a.longitude]}
            radius={a._flash?8:5}
            pathOptions={{
              pane: "alertPane",            // NEW
              color: a._flash?"gold":"red",
              fillOpacity: a._flash?0.85:0.65,
              weight: 1,
            }}>
            <Popup>
              <strong>{a.alert_type}</strong><br/>
              {a.timestamp}<br/>
              Severity: {a.severity ?? "?"}
            </Popup>
          </CircleMarker>
        ))}

        {/* hotspot centroids (blue) */}
        {clusters.map(f=>(
          <CircleMarker key={f.properties.cluster_id}
            center={[f.geometry.coordinates[1],f.geometry.coordinates[0]]}
            radius={10} pathOptions={{color:"blue"}}>
            <Popup>
              Hotspot #{f.properties.cluster_id}<br/>
              Alerts: {f.properties.count}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </>
  );
}
