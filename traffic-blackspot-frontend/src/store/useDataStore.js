import { create } from 'zustand';

const defaultFilters = {
  severity: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
  weather: 'all',
  riskThreshold: 0,
  dateRange: null,
};

export const useDataStore = create((set) => ({
  accidentData: [],
  topBlackSpots: [],
  isLoading: false,
  filters: defaultFilters,

  setFilters: (partial) =>
    set((state) => ({ filters: { ...state.filters, ...partial } })),

  resetFilters: () => set({ filters: defaultFilters }),

  loadData: (accidents, blackSpots) =>
    set({ accidentData: accidents, topBlackSpots: blackSpots, isLoading: false }),

  setLoading: (isLoading) => set({ isLoading }),
}));
