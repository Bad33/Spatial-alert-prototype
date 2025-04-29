
import "leaflet/dist/leaflet.css";
import L from "leaflet";
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:   new URL("leaflet/dist/images/marker-icon-2x.png", import.meta.url).href,
  iconUrl:         new URL("leaflet/dist/images/marker-icon.png",   import.meta.url).href,
  shadowUrl:       new URL("leaflet/dist/images/marker-shadow.png", import.meta.url).href,
});

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
