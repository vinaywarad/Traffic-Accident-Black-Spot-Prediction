import { useMemo } from 'react';
import { usePredictionStore } from '../store/usePredictionStore';

export function useModelPredictions() {
  const { predictions, selectedModel, sortField, sortDir, searchQuery, currentPage, pageSize } =
    usePredictionStore();

  const processed = useMemo(() => {
    let data = predictions.map((p) => ({
      ...p,
      activeScore: p.modelPredictions?.[selectedModel] ?? p.riskScore,
    }));

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      data = data.filter(
        (p) =>
          p.locationName?.toLowerCase().includes(q) ||
          p.roadName?.toLowerCase().includes(q) ||
          p.id?.toLowerCase().includes(q)
      );
    }

    data.sort((a, b) => {
      let av = a[sortField] ?? a.activeScore;
      let bv = b[sortField] ?? b.activeScore;
      if (typeof av === 'string') av = av.toLowerCase();
      if (typeof bv === 'string') bv = bv.toLowerCase();
      if (av < bv) return sortDir === 'asc' ? -1 : 1;
      if (av > bv) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });

    const total = data.length;
    const totalPages = Math.ceil(total / pageSize);
    const start = (currentPage - 1) * pageSize;
    const page = data.slice(start, start + pageSize);

    return { page, total, totalPages };
  }, [predictions, selectedModel, sortField, sortDir, searchQuery, currentPage, pageSize]);

  return processed;
}
