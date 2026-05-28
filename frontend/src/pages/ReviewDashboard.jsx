import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  Search, Filter, ChevronLeft, ChevronRight, Lock, Eye, AlertCircle, CheckCircle, HelpCircle
} from 'lucide-react';
import { recordsAPI } from '../api/endpoints';

export default function ReviewDashboard() {
  const [page, setPage] = useState(1);
  const [scope, setScope] = useState('');
  const [sourceType, setSourceType] = useState('');
  const [validationStatus, setValidationStatus] = useState('');
  const [reviewStatus, setReviewStatus] = useState('');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');

  // Debounce search input manually
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(search);
      setPage(1); // reset to page 1 on search
    }, 400);
    return () => clearTimeout(timer);
  }, [search]);

  // Load records
  const { data, isLoading, error } = useQuery({
    queryKey: ['records', page, scope, sourceType, validationStatus, reviewStatus, debouncedSearch],
    queryFn: () => recordsAPI.list({
      page,
      size: 15,
      scope: scope || undefined,
      source_type: sourceType || undefined,
      validation_status: validationStatus || undefined,
      review_status: reviewStatus || undefined,
      search: debouncedSearch || undefined
    }),
    keepPreviousData: true,
    refetchOnWindowFocus: false
  });

  const handleFilterChange = (setter, val) => {
    setter(val);
    setPage(1); // Reset page on filter change
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.9) return 'text-emerald-400';
    if (score >= 0.7) return 'text-blue-400';
    if (score >= 0.5) return 'text-amber-400';
    return 'text-red-400';
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">
          Analyst Review Console
        </h1>
        <p className="text-slate-400 mt-1">
          Audit, comment, and sign-off on emissions calculations before audit lock.
        </p>
      </div>

      {/* Filter Toolbar */}
      <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/80 flex flex-col lg:flex-row gap-4 items-stretch lg:items-center">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-3 h-4.5 w-4.5 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by invoice#, meter ID, travel code, cost center..."
            className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-lg py-2 pl-10 pr-4 text-sm placeholder-slate-500 text-white focus:outline-none"
          />
        </div>

        {/* Filters */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 shrink-0">
          {/* Scope */}
          <select
            value={scope}
            onChange={(e) => handleFilterChange(setScope, e.target.value)}
            className="bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-lg py-2 px-3 text-xs text-slate-300 focus:outline-none cursor-pointer"
          >
            <option value="">All Scopes</option>
            <option value="Scope 1">Scope 1</option>
            <option value="Scope 2">Scope 2</option>
            <option value="Scope 3">Scope 3</option>
          </select>

          {/* Source Type */}
          <select
            value={sourceType}
            onChange={(e) => handleFilterChange(setSourceType, e.target.value)}
            className="bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-lg py-2 px-3 text-xs text-slate-300 focus:outline-none cursor-pointer"
          >
            <option value="">All Sources</option>
            <option value="sap">SAP Fuel</option>
            <option value="utility">Utility Meter</option>
            <option value="travel">Travel API</option>
          </select>

          {/* Validation Status */}
          <select
            value={validationStatus}
            onChange={(e) => handleFilterChange(setValidationStatus, e.target.value)}
            className="bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-lg py-2 px-3 text-xs text-slate-300 focus:outline-none cursor-pointer"
          >
            <option value="">All Validations</option>
            <option value="validated">Clean / Validated</option>
            <option value="flagged">Flagged / Suspicious</option>
          </select>

          {/* Review Status */}
          <select
            value={reviewStatus}
            onChange={(e) => handleFilterChange(setReviewStatus, e.target.value)}
            className="bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-lg py-2 px-3 text-xs text-slate-300 focus:outline-none cursor-pointer"
          >
            <option value="">All Review States</option>
            <option value="pending">Pending Review</option>
            <option value="approved">Approved / Locked</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Main Records Table */}
      <div className="p-6 rounded-2xl glass-panel relative overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-brand-500"></div>
          </div>
        ) : error ? (
          <div className="text-red-400 text-sm py-4">Error loading records.</div>
        ) : data.items.length === 0 ? (
          <div className="text-slate-500 text-sm py-16 text-center border border-dashed border-slate-800 rounded-xl">
            No emission records match the selected filters.
          </div>
        ) : (
          <div className="space-y-4">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm border-collapse">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                    <th className="pb-3 text-xs font-bold uppercase tracking-wider">Date</th>
                    <th className="pb-3 text-xs font-bold uppercase tracking-wider">Source</th>
                    <th className="pb-3 text-xs font-bold uppercase tracking-wider">Activity</th>
                    <th className="pb-3 text-xs font-bold uppercase tracking-wider">Scope</th>
                    <th className="pb-3 text-xs font-bold uppercase tracking-wider">Emissions</th>
                    <th className="pb-3 text-xs font-bold uppercase tracking-wider">Confidence</th>
                    <th className="pb-3 text-xs font-bold uppercase tracking-wider">Validation</th>
                    <th className="pb-3 text-xs font-bold uppercase tracking-wider">Sign-Off</th>
                    <th className="pb-3 text-xs font-bold uppercase tracking-wider text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/40">
                  {data.items.map((rec) => (
                    <tr key={rec.id} className="hover:bg-slate-900/30 group">
                      {/* Transaction Date */}
                      <td className="py-3.5 text-slate-300 font-medium">
                        {rec.transaction_date || 'N/A'}
                      </td>
                      
                      {/* Source */}
                      <td className="py-3.5 capitalize text-slate-400 text-xs">
                        {rec.source_type}
                      </td>

                      {/* Activity & Reference */}
                      <td className="py-3.5">
                        <div className="font-semibold text-slate-200 text-sm">{rec.activity_type}</div>
                        <div className="text-slate-500 text-xs truncate max-w-[150px]">
                          Ref: {rec.source_reference || 'N/A'}
                        </div>
                      </td>

                      {/* Scope */}
                      <td className="py-3.5">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          rec.scope === 'Scope 1' ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-900/60' :
                          rec.scope === 'Scope 2' ? 'bg-blue-950/40 text-blue-400 border border-blue-900/60' :
                          'bg-purple-950/40 text-purple-400 border border-purple-900/60'
                        }`}>
                          {rec.scope}
                        </span>
                      </td>

                      {/* Estimated Emissions */}
                      <td className="py-3.5">
                        <div className="font-extrabold text-slate-200 text-sm">
                          {rec.estimated_emissions ? `${rec.estimated_emissions.toLocaleString(undefined, {maximumFractionDigits: 1})} kg` : 'Err / N/A'}
                        </div>
                        <div className="text-slate-500 text-xs">
                          {rec.amount ? `${rec.amount} ${rec.original_unit}` : ''}
                        </div>
                      </td>

                      {/* Confidence */}
                      <td className="py-3.5">
                        <div className="flex items-center gap-1.5">
                          <span className={`font-bold text-sm ${getConfidenceColor(rec.confidence_score)}`}>
                            {Math.round(rec.confidence_score * 100)}%
                          </span>
                        </div>
                      </td>

                      {/* Validation Status */}
                      <td className="py-3.5">
                        {rec.validation_status === 'validated' ? (
                          <span className="inline-flex items-center gap-1 text-emerald-400 text-xs font-semibold">
                            <CheckCircle className="h-3.5 w-3.5" /> Validated
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-amber-500 text-xs font-semibold" title="Data anomalies or duplicate alerts detected">
                            <AlertCircle className="h-3.5 w-3.5" /> Flagged
                          </span>
                        )}
                      </td>

                      {/* Review Status */}
                      <td className="py-3.5">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${
                          rec.review_status === 'approved' ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-800/80' :
                          rec.review_status === 'rejected' ? 'bg-red-950/40 text-red-400 border border-red-800/80' :
                          'bg-indigo-950/40 text-indigo-400 border border-indigo-800/80'
                        }`}>
                          {rec.review_status}
                        </span>
                      </td>

                      {/* Action */}
                      <td className="py-3.5 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {rec.locked_for_audit && (
                            <Lock className="h-3.5 w-3.5 text-slate-500" title="Locked for Audit Integrity" />
                          )}
                          <Link
                            to={`/records/${rec.id}`}
                            className="p-1.5 rounded-md hover:bg-slate-800 hover:text-white text-slate-400 transition-all flex items-center gap-1.5 text-xs font-bold"
                          >
                            <Eye className="h-3.5 w-3.5" /> Review
                          </Link>
                        </div>
                      </td>

                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center justify-between border-t border-slate-800 pt-4 mt-6">
              <span className="text-xs text-slate-500">
                Showing page {data.page} of {Math.ceil(data.total / 15) || 1} ({data.total} total items)
              </span>
              <div className="flex items-center gap-2">
                <button
                  disabled={page === 1}
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronLeft className="h-4 w-4" />
                </button>
                <button
                  disabled={page * 15 >= data.total}
                  onClick={() => setPage(p => p + 1)}
                  className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
                >
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

    </div>
  );
}
