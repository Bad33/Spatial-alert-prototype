import { useEffect } from "react";
import { useMap } from "react-leaflet";
import "leaflet.heat";

export default function HeatLayer({ points, max }) {
  const map = useMap();

  useEffect(() => {
    if (!points.length) return;
    // leaflet.heat expects [lat, lon, intensity]
    const heat = L.heatLayer(points, {
      radius: 15,
      blur: 20,
      maxZoom: 17,
      max: max || Math.max(...points.map((p) => p[2])),
    }).addTo(map);

    return () => {
      map.removeLayer(heat);
    };
  }, [points, max, map]);

  return null; // this component adds layer via side-effect
}
