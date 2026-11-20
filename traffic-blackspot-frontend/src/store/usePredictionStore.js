import { create } from 'zustand';

export const usePredictionStore = create((set) => ({
  selectedModel: 'xgboost',
  setSelectedModel: (model) => set({ selectedModel: model }),

  predictions: [],
  setPredictions: (predictions) => set({ predictions }),

  sortField: 'riskScore',
  sortDir: 'desc',
  setSort: (field) =>
    set((s) => ({
      sortField: field,
      sortDir: s.sortField === field && s.sortDir === 'desc' ? 'asc' : 'desc',
    })),

  searchQuery: '',
  setSearchQuery: (q) => set({ searchQuery: q }),

  currentPage: 1,
  setCurrentPage: (page) => set({ currentPage: page }),

  pageSize: 20,
}));
