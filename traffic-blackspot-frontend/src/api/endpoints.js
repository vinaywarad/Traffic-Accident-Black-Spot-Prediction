/**
 * Single source of truth for all API endpoint paths.
 * Change the backend route once here — updates everywhere.
 */
export const ENDPOINTS = {
  // Health
  HEALTH:            '/health',
  HEALTH_DETAILED:   '/health/detailed',

  // Predictions
  PREDICT:           '/predict',
  PREDICT_BATCH:     '/predict/batch',

  // Black spots
  BLACKSPOTS:        '/blackspots',
  BLACKSPOT_BY_ID:   (id) => `/blackspots/${id}`,

  // Models
  MODELS:            '/models',

  // Analytics
  ANALYTICS_SUMMARY: '/analytics/summary',
  ANALYTICS_HEATMAP: '/analytics/heatmap',
  ANALYTICS_TRENDS:  '/analytics/trends',
}
