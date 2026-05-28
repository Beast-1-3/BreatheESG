import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line
} from 'recharts';
import { 
  TrendingUp, FileText, AlertTriangle, CheckCircle, RefreshCw, PlusCircle, ArrowUpRight 
} from 'lucide-react';
import { dashboardAPI } from '../api/endpoints';

export default function Dashboard() {
  const { data: summary, isLoading, error, refetch, isRefetching } = useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: dashboardAPI.summary,
    refetchOnWindowFocus: false
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-brand-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 rounded-xl bg-red-950/40 border border-red-900/50 text-red-400">
        Error loading dashboard data: {error.message}. Make sure the backend server is running.
      </div>
    );
  }

  // Format charts source breakdown data
  const sourceChartData = Object.entries(summary.source_breakdown).map(([name, value]) => ({
    name: name.toUpperCase(),
    records: value
  }));

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Ingestion & Calculation Hub
          </h1>
          <p className="text-slate-400 mt-1">
            Real-time multi-source data status and scope estimates.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-200 transition-all active:scale-[0.98]"
          >
            <RefreshCw className={`h-4 w-4 ${isRefetching ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <Link
            to="/uploads"
            className="flex items-center gap-2 px-4 py-2 text-sm font-semibold rounded-lg bg-brand-600 hover:bg-brand-500 text-white shadow-lg shadow-brand-900/20 transition-all active:scale-[0.98]"
          >
            <PlusCircle className="h-4 w-4" />
            Ingest Data
          </Link>
        </div>
      </div>

      {/* Metric Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="p-6 rounded-2xl glass-panel relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-brand-500"></div>
          <p className="text-xs font-bold uppercase text-slate-400 tracking-wider">
            Total Carbon Footprint
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-extrabold text-white">
              {(summary.total_emissions_kg / 1000).toFixed(2)}
            </span>
            <span className="text-sm font-medium text-slate-400">t CO2e</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            {summary.total_emissions_kg.toLocaleString()} kg CO2e computed
          </p>
        </div>

        <div className="p-6 rounded-2xl glass-panel relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-blue-500"></div>
          <p className="text-xs font-bold uppercase text-slate-400 tracking-wider">
            Ingested Records
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-extrabold text-white">
              {summary.record_count}
            </span>
            <span className="text-sm font-medium text-slate-400">rows</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-1">
            <CheckCircle className="h-3 w-3 text-emerald-400" />
            <span>Across 3 Data Sources</span>
          </div>
        </div>

        <div className="p-6 rounded-2xl glass-panel relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-amber-500"></div>
          <p className="text-xs font-bold uppercase text-slate-400 tracking-wider">
            Flagged & Suspicious
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-extrabold text-amber-400">
              {summary.validation_status_breakdown.flagged || 0}
            </span>
            <span className="text-sm font-medium text-slate-400">records</span>
          </div>
          <div className="flex items-center gap-1 text-xs text-amber-500 mt-1">
            <AlertTriangle className="h-3.5 w-3.5" />
            <span>Requires Analyst Review</span>
          </div>
        </div>

        <div className="p-6 rounded-2xl glass-panel relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-indigo-500"></div>
          <p className="text-xs font-bold uppercase text-slate-400 tracking-wider">
            Pending Sign-Off
          </p>
          <div className="flex items-baseline gap-2 mt-2">
            <span className="text-3xl font-extrabold text-indigo-400">
              {summary.review_status_breakdown.pending || 0}
            </span>
            <span className="text-sm font-medium text-slate-400">pending</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Approved: {summary.review_status_breakdown.approved || 0} | Rejected: {summary.review_status_breakdown.rejected || 0}
          </p>
        </div>
      </div>

      {/* Scope Details Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scope 1 */}
        <div className="p-6 rounded-2xl glass-panel border-t-4 border-emerald-500">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-extrabold text-lg text-white">Scope 1</h3>
              <p className="text-xs text-slate-400">Direct Fuel & Combustion</p>
            </div>
            <span className="px-2.5 py-0.5 rounded-full bg-emerald-950/40 text-emerald-400 border border-emerald-800 text-[10px] font-bold">
              SAP
            </span>
          </div>
          <div className="mt-4">
            <div className="text-2xl font-black text-white">
              {(summary.scope_breakdown["Scope 1"].emissions / 1000).toFixed(2)} t
            </div>
            <div className="text-xs text-slate-500 mt-0.5">
              {summary.scope_breakdown["Scope 1"].count} records normalized
            </div>
          </div>
        </div>

        {/* Scope 2 */}
        <div className="p-6 rounded-2xl glass-panel border-t-4 border-blue-500">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-extrabold text-lg text-white">Scope 2</h3>
              <p className="text-xs text-slate-400">Indirect Purchased Electricity</p>
            </div>
            <span className="px-2.5 py-0.5 rounded-full bg-blue-950/40 text-blue-400 border border-blue-800 text-[10px] font-bold">
              Utility Meter
            </span>
          </div>
          <div className="mt-4">
            <div className="text-2xl font-black text-white">
              {(summary.scope_breakdown["Scope 2"].emissions / 1000).toFixed(2)} t
            </div>
            <div className="text-xs text-slate-500 mt-0.5">
              {summary.scope_breakdown["Scope 2"].count} records normalized
            </div>
          </div>
        </div>

        {/* Scope 3 */}
        <div className="p-6 rounded-2xl glass-panel border-t-4 border-purple-500">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-extrabold text-lg text-white">Scope 3</h3>
              <p className="text-xs text-slate-400">Business Travel & Hotels</p>
            </div>
            <span className="px-2.5 py-0.5 rounded-full bg-purple-950/40 text-purple-400 border border-purple-800 text-[10px] font-bold">
              Navan/Concur API
            </span>
          </div>
          <div className="mt-4">
            <div className="text-2xl font-black text-white">
              {(summary.scope_breakdown["Scope 3"].emissions / 1000).toFixed(2)} t
            </div>
            <div className="text-xs text-slate-500 mt-0.5">
              {summary.scope_breakdown["Scope 3"].count} records normalized
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Chart */}
        <div className="p-6 rounded-2xl glass-panel lg:col-span-2 flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-lg text-white mb-1">
              Monthly Emissions Breakdown
            </h3>
            <p className="text-xs text-slate-400 mb-6">
              GHG Scope emissions trends over current accounting period (kg CO2e).
            </p>
          </div>
          <div className="h-80 w-full">
            {summary.monthly_emissions.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={summary.monthly_emissions}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }}
                  />
                  <Legend verticalAlign="top" height={36} />
                  <Line type="monotone" dataKey="Scope 1" stroke="#22c55e" strokeWidth={2.5} name="Scope 1" dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="Scope 2" stroke="#3b82f6" strokeWidth={2.5} name="Scope 2" dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="Scope 3" stroke="#a855f7" strokeWidth={2.5} name="Scope 3" dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-slate-500 border border-dashed border-slate-800 rounded-xl">
                No monthly data found. Go to Upload Center to ingest some files.
              </div>
            )}
          </div>
        </div>

        {/* Source Ingestion Split */}
        <div className="p-6 rounded-2xl glass-panel flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-lg text-white mb-1">
              Ingestion Sources
            </h3>
            <p className="text-xs text-slate-400 mb-6">
              Row distributions per integrated enterprise system.
            </p>
          </div>
          <div className="h-80 w-full">
            {summary.record_count > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sourceChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#fff' }}
                  />
                  <Bar dataKey="records" fill="#10b981" radius={[4, 4, 0, 0]} barSize={40} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-sm text-slate-500 border border-dashed border-slate-800 rounded-xl">
                No source records.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Review Quick Action Panel */}
      <div className="p-6 rounded-2xl glass-panel bg-gradient-to-r from-slate-900 via-slate-900 to-brand-950/20 border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="font-bold text-white text-base">
            Needs Sign-Off
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            You have {summary.review_status_breakdown.pending || 0} normalized records awaiting analyst approval.
          </p>
        </div>
        <Link
          to="/review"
          className="flex items-center gap-1 text-sm font-bold text-brand-400 hover:text-brand-300 transition-all"
        >
          Open Review Console
          <ArrowUpRight className="h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
