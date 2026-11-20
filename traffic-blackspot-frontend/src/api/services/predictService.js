import apiClient from '../client'
import { ENDPOINTS } from '../endpoints'

/**
 * Predict risk for a single location.
 * Used by: map click handler, manual prediction form.
 */
export const predictSingle = async (locationData) => {
  const { data } = await apiClient.post(ENDPOINTS.PREDICT, locationData)
  return data
}

/**
 * Predict risk for multiple locations at once (up to 500).
 * Used by: map page on load to score all road segments.
 */
export const predictBatch = async (records, modelName = 'best') => {
  const { data } = await apiClient.post(ENDPOINTS.PREDICT_BATCH, {
    records,
    model_name: modelName,
  })
  return data
}

/**
 * Build a prediction request object from lat/lng + defaults.
 * Used when user clicks a point on the map.
 */
export const buildPredictionRequest = (lat, lng, overrides = {}) => {
  const now   = new Date()
  const hour  = now.getHours()
  const month = now.getMonth() + 1
  const day   = now.getDay()
  const adjustedDay = day === 0 ? 6 : day - 1

  return {
    latitude:          lat,
    longitude:         lng,
    hour,
    month,
    day_of_week:       adjustedDay,
    road_type:         overrides.road_type   || 'City_Road',
    weather:           overrides.weather     || 'Clear',
    speed_limit:       overrides.speed_limit || 40,
    vehicles_involved: overrides.vehicles    || 1,
    ...overrides,
  }
}

/**
 * Generate batch prediction records for Bengaluru road corridors.
 * Used to populate the heatmap on map page load.
 */
export const generateBengaluruGrid = (density = 'medium') => {
  const counts = { low: 30, medium: 80, high: 150 }
  const n = counts[density] || 80

  const corridors = [
    { latRange: [12.90, 12.96], lngRange: [77.60, 77.70], road_type: 'ORR',       speed_limit: 80 },
    { latRange: [12.97, 12.98], lngRange: [77.59, 77.62], road_type: 'City_Road', speed_limit: 40 },
    { latRange: [12.84, 12.95], lngRange: [77.65, 77.68], road_type: 'NH',        speed_limit: 60 },
    { latRange: [13.00, 13.08], lngRange: [77.58, 77.61], road_type: 'NH',        speed_limit: 60 },
    { latRange: [13.00, 13.05], lngRange: [77.50, 77.55], road_type: 'NH',        speed_limit: 60 },
    { latRange: [12.96, 12.99], lngRange: [77.73, 77.78], road_type: 'City_Road', speed_limit: 40 },
  ]

  const now   = new Date()
  const hour  = now.getHours()
  const month = now.getMonth() + 1
  const dow   = now.getDay() === 0 ? 6 : now.getDay() - 1

  const records = []
  const perCorridor = Math.ceil(n / corridors.length)

  corridors.forEach((corridor) => {
    for (let i = 0; i < perCorridor; i++) {
      const lat = corridor.latRange[0] + Math.random() * (corridor.latRange[1] - corridor.latRange[0])
      const lng = corridor.lngRange[0] + Math.random() * (corridor.lngRange[1] - corridor.lngRange[0])
      records.push({
        latitude:          parseFloat(lat.toFixed(6)),
        longitude:         parseFloat(lng.toFixed(6)),
        hour,
        month,
        day_of_week:       dow,
        road_type:         corridor.road_type,
        weather:           month >= 6 && month <= 9 ? 'Rainy' : 'Clear',
        speed_limit:       corridor.speed_limit,
        vehicles_involved: Math.floor(Math.random() * 3) + 1,
      })
    }
  })

  return records.slice(0, n)
}
