import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { MapContainer, TileLayer, useMap } from 'react-leaflet'
import { useEffect } from 'react'
import { useMapStore } from '../../store/useMapStore'
import BlackSpotMarker from './BlackSpotMarker'

// Fix default icon issue
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconUrl:       'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl:     'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

const TILE_URL  = 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
const TILE_ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
const BENGALURU = [12.9716, 77.5946]

/** Renders a Leaflet heatmap from live batch prediction results */
function HeatmapLayer({ predictions }) {
  const map = useMap()

  useEffect(() => {
    if (!predictions?.length || !window.L?.heatLayer) return

    const heatData = predictions
      .filter((p) => p.risk_score > 0.2)
      .map((p) => [p.location.latitude, p.location.longitude, p.risk_score])

    const layer = L.heatLayer(heatData, {
      radius:  25,
      blur:    15,
      maxZoom: 17,
      max:     1.0,
      gradient: {
        0.2: '#22C55E',
        0.4: '#F59E0B',
        0.6: '#F97316',
        0.8: '#EF4444',
        1.0: '#DC2626',
      },
    })
    layer.addTo(map)
    return () => { try { map.removeLayer(layer) } catch (_) {} }
  }, [predictions, map])

  return null
}

export default function AccidentMap({
  height = '100%',
  style,
  predictions = [],
  blackspots  = [],
}) {
  const { activeLayers, setSelectedBlackspot } = useMapStore()

  return (
    <MapContainer
      center={BENGALURU}
      zoom={11}
      style={{ height, width: '100%', borderRadius: 'inherit', ...style }}
      zoomControl={true}
    >
      <TileLayer url={TILE_URL} attribution={TILE_ATTR} />

      {/* Live heatmap from batch predictions */}
      {activeLayers.heatmap && predictions.length > 0 && (
        <HeatmapLayer predictions={predictions} />
      )}

      {/* Known black spot markers from API */}
      {activeLayers.blackspots && blackspots.map((spot) => (
        <BlackSpotMarker
          key={spot.id}
          spot={spot}
          onClick={() => setSelectedBlackspot(spot)}
        />
      ))}
    </MapContainer>
  )
}
