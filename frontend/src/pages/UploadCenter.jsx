import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  UploadCloud, RefreshCw, CheckCircle2, AlertOctagon, FileText, Database, ShieldCheck 
} from 'lucide-react';
import { uploadsAPI } from '../api/endpoints';

export default function UploadCenter() {
  const queryClient = useQueryClient();
  const [sapFile, setSapFile] = useState(null);
  const [utilityFile, setUtilityFile] = useState(null);
  const [uploadError, setUploadError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Queries for history and active datasources
  const { data: history = [], isLoading: historyLoading } = useQuery({
    queryKey: ['uploadHistory'],
    queryFn: uploadsAPI.getHistory
  });

  const { data: dataSources = [] } = useQuery({
    queryKey: ['dataSources'],
    queryFn: uploadsAPI.getDataSources
  });

  // Ingestion Mutations
  const sapMutation = useMutation({
    mutationFn: uploadsAPI.uploadSap,
    onSuccess: (data) => {
      setSuccessMsg(`SAP File Ingested: ${data.filename} has been queued and processed.`);
      setSapFile(null);
      setUploadError('');
      queryClient.invalidateQueries(['uploadHistory']);
      queryClient.invalidateQueries(['dashboardSummary']);
    },
    onError: (err) => {
      setUploadError(err.response?.data?.detail || 'SAP CSV ingestion failed.');
    }
  });

  const utilityMutation = useMutation({
    mutationFn: uploadsAPI.uploadUtility,
    onSuccess: (data) => {
      setSuccessMsg(`Utility File Ingested: ${data.filename} has been queued and processed.`);
      setUtilityFile(null);
      setUploadError('');
      queryClient.invalidateQueries(['uploadHistory']);
      queryClient.invalidateQueries(['dashboardSummary']);
    },
    onError: (err) => {
      setUploadError(err.response?.data?.detail || 'Utility CSV ingestion failed.');
    }
  });

  const travelSyncMutation = useMutation({
    mutationFn: uploadsAPI.syncTravel,
    onSuccess: (data) => {
      setSuccessMsg(`REST Travel API Sync Complete: simulated Navan/Concur feed processed.`);
      setUploadError('');
      queryClient.invalidateQueries(['uploadHistory']);
      queryClient.invalidateQueries(['dashboardSummary']);
    },
    onError: (err) => {
      setUploadError(err.response?.data?.detail || 'Travel REST sync failed.');
    }
  });

  const handleSapUpload = (e) => {
    e.preventDefault();
    if (!sapFile) return;
    sapMutation.mutate(sapFile);
  };

  const handleUtilityUpload = (e) => {
    e.preventDefault();
    if (!utilityFile) return;
    utilityMutation.mutate(utilityFile);
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">
          Data Connection & Upload Center
        </h1>
        <p className="text-slate-400 mt-1">
          Ingest fuel, electricity utility logs, or sync travel payloads.
        </p>
      </div>

      {/* Notifications */}
      {uploadError && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-900/50 text-sm text-red-400 flex items-center gap-3">
          <AlertOctagon className="h-5 w-5 shrink-0" />
          <div>{uploadError}</div>
        </div>
      )}

      {successMsg && (
        <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-900/50 text-sm text-emerald-400 flex items-center gap-3">
          <CheckCircle2 className="h-5 w-5 shrink-0" />
          <div>{successMsg}</div>
        </div>
      )}

      {/* Active Data Sources Grid */}
      <div>
        <h2 className="text-lg font-bold text-white mb-4">Active System Configs</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {dataSources.map(ds => (
            <div key={ds.id} className="p-4 rounded-xl bg-slate-900/40 border border-slate-800 flex items-start gap-3">
              <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700">
                <Database className="h-4.5 w-4.5 text-brand-400" />
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-200">{ds.name}</h4>
                <p className="text-xs text-slate-500 capitalize">Type: {ds.source_type}</p>
                <div className="flex items-center gap-1 mt-1 text-[10px] font-bold text-emerald-400">
                  <ShieldCheck className="h-3 w-3" /> Enabled
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Ingestion Actions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* SAP Upload */}
        <div className="p-6 rounded-2xl glass-panel flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-white text-base">SAP Ingestion</h3>
            <p className="text-xs text-slate-400 mt-1">
              Supports CSV extracts containing plant code fuel transactions (German or English).
            </p>
          </div>
          
          <form onSubmit={handleSapUpload} className="mt-6 space-y-4">
            <div className="border-2 border-dashed border-slate-800 hover:border-brand-500/50 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer transition-all bg-slate-950/50 relative">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => {
                  setSapFile(e.target.files[0]);
                  setSuccessMsg('');
                  setUploadError('');
                }}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <UploadCloud className="h-8 w-8 text-slate-500 mb-2" />
              <span className="text-xs font-semibold text-slate-300">
                {sapFile ? sapFile.name : 'Select CSV file'}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5">Max size 10MB</span>
            </div>
            
            <button
              type="submit"
              disabled={!sapFile || sapMutation.isLoading}
              className="w-full py-2 bg-slate-800 border border-slate-700 hover:bg-brand-600 hover:border-brand-500 hover:text-white rounded-lg text-xs font-bold transition-all text-slate-200"
            >
              {sapMutation.isLoading ? 'Uploading...' : 'Upload SAP Export'}
            </button>
          </form>
        </div>

        {/* Utility Portal Upload */}
        <div className="p-6 rounded-2xl glass-panel flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-white text-base">Utility Ingestion</h3>
            <p className="text-xs text-slate-400 mt-1">
              Supports CSV bills containing meter billing periods, kWh consumption, and tariffs.
            </p>
          </div>
          
          <form onSubmit={handleUtilityUpload} className="mt-6 space-y-4">
            <div className="border-2 border-dashed border-slate-800 hover:border-brand-500/50 rounded-xl p-4 flex flex-col items-center justify-center cursor-pointer transition-all bg-slate-950/50 relative">
              <input
                type="file"
                accept=".csv"
                onChange={(e) => {
                  setUtilityFile(e.target.files[0]);
                  setSuccessMsg('');
                  setUploadError('');
                }}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              />
              <UploadCloud className="h-8 w-8 text-slate-500 mb-2" />
              <span className="text-xs font-semibold text-slate-300">
                {utilityFile ? utilityFile.name : 'Select CSV file'}
              </span>
              <span className="text-[10px] text-slate-500 mt-0.5">Max size 10MB</span>
            </div>
            
            <button
              type="submit"
              disabled={!utilityFile || utilityMutation.isLoading}
              className="w-full py-2 bg-slate-800 border border-slate-700 hover:bg-brand-600 hover:border-brand-500 hover:text-white rounded-lg text-xs font-bold transition-all text-slate-200"
            >
              {utilityMutation.isLoading ? 'Uploading...' : 'Upload Utility Bill'}
            </button>
          </form>
        </div>

        {/* REST Travel Sync */}
        <div className="p-6 rounded-2xl glass-panel flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-white text-base">Travel API Sync</h3>
            <p className="text-xs text-slate-400 mt-1">
              Syncs travel logs (flights, hotels, taxis) from Navan/Concur database feed.
            </p>
          </div>
          
          <div className="mt-6 space-y-4">
            <div className="border border-slate-800/80 rounded-xl p-4 flex flex-col items-center justify-center bg-slate-950/30">
              <RefreshCw className={`h-8 w-8 text-brand-400 mb-2 ${travelSyncMutation.isLoading ? 'animate-spin' : ''}`} />
              <span className="text-xs font-bold text-slate-200">REST API Integration</span>
              <span className="text-[10px] text-slate-500 mt-1">Status: Active Connector</span>
            </div>
            
            <button
              type="button"
              onClick={() => {
                setSuccessMsg('');
                setUploadError('');
                travelSyncMutation.mutate();
              }}
              disabled={travelSyncMutation.isLoading}
              className="w-full py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-bold transition-all active:scale-[0.98]"
            >
              {travelSyncMutation.isLoading ? 'Syncing Bookings...' : 'Trigger Sync Now'}
            </button>
          </div>
        </div>

      </div>

      {/* Upload History Table */}
      <div className="p-6 rounded-2xl glass-panel">
        <h3 className="font-extrabold text-white text-lg mb-4">Ingestion Run Logs</h3>
        {historyLoading ? (
          <div className="text-slate-400 text-sm">Loading logs...</div>
        ) : history.length === 0 ? (
          <div className="text-slate-500 text-sm py-4 border border-dashed border-slate-800 rounded-xl text-center">
            No previous uploads found. Perform an ingestion run above to start.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 font-semibold">
                  <th className="pb-3 text-xs font-bold uppercase tracking-wider">File / Run Reference</th>
                  <th className="pb-3 text-xs font-bold uppercase tracking-wider">Ingested At</th>
                  <th className="pb-3 text-xs font-bold uppercase tracking-wider">Data Size</th>
                  <th className="pb-3 text-xs font-bold uppercase tracking-wider">Status</th>
                  <th className="pb-3 text-xs font-bold uppercase tracking-wider">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40">
                {history.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-900/30">
                    <td className="py-4 font-semibold text-slate-200 flex items-center gap-2">
                      <FileText className="h-4 w-4 text-slate-500" />
                      {run.filename || 'REST API Sync'}
                    </td>
                    <td className="py-4 text-slate-400">
                      {new Date(run.created_at).toLocaleString()}
                    </td>
                    <td className="py-4 text-slate-400">
                      {run.file_size ? `${(run.file_size / 1024).toFixed(1)} KB` : 'JSON API'}
                    </td>
                    <td className="py-4">
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold ${
                        run.status === 'processed'
                          ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-800'
                          : 'bg-red-950/40 text-red-400 border border-red-800'
                      }`}>
                        {run.status}
                      </span>
                    </td>
                    <td className="py-4 text-xs text-slate-500 max-w-xs truncate">
                      {run.error_message || 'Successful parsing & normalization.'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

    </div>
  );
}
