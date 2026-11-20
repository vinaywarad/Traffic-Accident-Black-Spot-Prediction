import { create } from 'zustand'

export const useMapStore = create((set) => ({
  // Existing state
  selectedPoint:    null,
  drawerOpen:       false,
  mapCenter:        [12.9716, 77.5946],
  mapZoom:          11,
  showMarkers:      true,

  // Live prediction results from batch API
  livePredictions:  [],
  isLoadingPreds:   false,
  predictionError:  null,

  // Selected black spot for detail drawer
  selectedBlackspot: null,

  // Active filters
  activeFilters: { severity: 'all', weather: 'all' },

  // Active layers
  activeLayers: { heatmap: true, markers: true, blackspots: true },

  // Actions
  setLivePredictions:   (preds) => set({ livePredictions: preds }),
  setSelectedPoint:     (pt)    => set({ selectedPoint: pt, drawerOpen: !!pt }),
  setSelectedBlackspot: (bs)    => set({ selectedBlackspot: bs, drawerOpen: !!bs }),
  setDrawerOpen:        (open)  => set({ drawerOpen: open }),
  setMapView:           (center, zoom) => set({ mapCenter: center, mapZoom: zoom }),
  toggleMarkers:        ()      => set((s) => ({ showMarkers: !s.showMarkers })),

  setFilter: (key, value) => set((s) => ({
    activeFilters: { ...s.activeFilters, [key]: value },
  })),

  toggleLayer: (layer) => set((s) => ({
    activeLayers: { ...s.activeLayers, [layer]: !s.activeLayers[layer] },
  })),

  clearSelection: () => set({ selectedPoint: null, selectedBlackspot: null, drawerOpen: false }),
}))
