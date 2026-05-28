import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  ArrowLeft, Lock, ShieldAlert, CheckCircle, AlertTriangle, MessageSquare, History, Play
} from 'lucide-react';
import { recordsAPI, reviewsAPI } from '../api/endpoints';

export default function RecordDetail() {
  const { id } = useParams();
  const queryClient = useQueryClient();
  const [commentText, setCommentText] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  // Fetch record details
  const { data: record, isLoading, error } = useQuery({
    queryKey: ['recordDetail', id],
    queryFn: () => recordsAPI.get(id),
    refetchOnWindowFocus: false
  });

  // Review Mutations
  const approveMutation = useMutation({
    mutationFn: (text) => reviewsAPI.approve(id, text),
    onSuccess: () => {
      setCommentText('');
      setErrorMsg('');
      queryClient.invalidateQueries(['recordDetail', id]);
      queryClient.invalidateQueries(['records']);
    },
    onError: (err) => {
      setErrorMsg(err.response?.data?.detail || 'Approval failed.');
    }
  });

  const rejectMutation = useMutation({
    mutationFn: (text) => reviewsAPI.reject(id, text),
    onSuccess: () => {
      setCommentText('');
      setErrorMsg('');
      queryClient.invalidateQueries(['recordDetail', id]);
      queryClient.invalidateQueries(['records']);
    },
    onError: (err) => {
      setErrorMsg(err.response?.data?.detail || 'Rejection failed.');
    }
  });

  const commentMutation = useMutation({
    mutationFn: (text) => reviewsAPI.addComment(id, text),
    onSuccess: () => {
      setCommentText('');
      setErrorMsg('');
      queryClient.invalidateQueries(['recordDetail', id]);
    },
    onError: (err) => {
      setErrorMsg(err.response?.data?.detail || 'Adding comment failed.');
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-brand-500"></div>
      </div>
    );
  }

  if (error || !record) {
    return (
      <div className="p-4 rounded-xl bg-red-950/40 border border-red-900/50 text-red-400">
        Error loading record details. Make sure the record ID is correct.
      </div>
    );
  }

  const handleApprove = () => {
    approveMutation.mutate(commentText);
  };

  const handleReject = () => {
    if (!commentText.trim()) {
      setErrorMsg('A review comment explaining the rejection is required.');
      return;
    }
    rejectMutation.mutate(commentText);
  };

  const handleAddCommentOnly = () => {
    if (!commentText.trim()) return;
    commentMutation.mutate(commentText);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Back Navigation */}
      <Link
        to="/review"
        className="inline-flex items-center gap-1.5 text-xs font-bold text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="h-4 w-4" /> Back to Review Console
      </Link>

      {/* Detail Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-extrabold text-white">
              {record.activity_type} Transaction
            </h1>
            <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
              record.scope === 'Scope 1' ? 'bg-emerald-950/40 text-emerald-400 border border-emerald-900/60' :
              record.scope === 'Scope 2' ? 'bg-blue-950/40 text-blue-400 border border-blue-900/60' :
              'bg-purple-950/40 text-purple-400 border border-purple-900/60'
            }`}>
              {record.scope}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Database Reference ID: {record.id}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {record.locked_for_audit ? (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-800/80 text-emerald-400 text-xs font-extrabold shadow-sm uppercase tracking-wider">
              <Lock className="h-4 w-4" /> Locked for Audit Integrity
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-950/40 border border-amber-800/80 text-amber-500 text-xs font-extrabold shadow-sm uppercase tracking-wider">
              <ShieldAlert className="h-4 w-4 animate-pulse" /> Awaiting Analyst Review
            </div>
          )}
        </div>
      </div>

      {errorMsg && (
        <div className="p-3.5 rounded-xl bg-red-950/40 border border-red-900/50 text-xs font-semibold text-red-400">
          {errorMsg}
        </div>
      )}

      {/* Side-by-Side: Raw Data vs. Normalized Calculations */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Raw Ingestion Payload */}
        <div className="p-6 rounded-2xl glass-panel flex flex-col justify-between">
          <div>
            <h3 className="font-extrabold text-white text-base mb-1">
              Raw Source Ingestion
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Original data payload as exported from {record.source_type.toUpperCase()}.
            </p>
          </div>
          
          <div className="flex-1 bg-slate-950/80 border border-slate-900 rounded-xl p-4 font-mono text-xs overflow-auto max-h-[300px]">
            {record.raw_record ? (
              <pre className="text-slate-300 leading-relaxed">
                {JSON.stringify(record.raw_record.raw_payload, null, 2)}
              </pre>
            ) : (
              <span className="text-slate-500 italic">No raw record logged.</span>
            )}
          </div>
          <div className="mt-4 text-[10px] text-slate-500">
            Row #{record.raw_record?.row_index || 0} in upload logs.
          </div>
        </div>

        {/* Normalized ESG Properties */}
        <div className="p-6 rounded-2xl glass-panel">
          <h3 className="font-extrabold text-white text-base mb-4">
            Normalized ESG Schema
          </h3>
          
          <div className="space-y-3.5">
            {/* Emissions Value */}
            <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800/80 flex items-center justify-between">
              <div>
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Estimated Carbon Emissions</div>
                <div className="text-xl font-black text-white mt-0.5">
                  {record.estimated_emissions ? `${record.estimated_emissions.toLocaleString(undefined, {maximumFractionDigits: 2})} kg CO2e` : 'Failed Calculation / N/A'}
                </div>
              </div>
              <div className="text-right">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Emission Factor</div>
                <div className="text-sm font-semibold text-slate-200 mt-1">
                  {record.emission_factor || 'N/A'} <span className="text-[10px] text-slate-500">kg/unit</span>
                </div>
              </div>
            </div>

            {/* Calculations Breakdown */}
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3.5 rounded-xl bg-slate-900/30 border border-slate-800/60">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Original Input</div>
                <div className="text-sm font-semibold text-slate-200 mt-1">
                  {record.amount || 'N/A'} {record.original_unit || ''}
                </div>
              </div>
              <div className="p-3.5 rounded-xl bg-slate-900/30 border border-slate-800/60">
                <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Normalized Value</div>
                <div className="text-sm font-semibold text-slate-200 mt-1">
                  {record.normalized_value ? `${record.normalized_value.toLocaleString(undefined, {maximumFractionDigits: 2})} ${record.normalized_unit}` : 'N/A'}
                </div>
              </div>
            </div>

            {/* Ingestion Meta */}
            <div className="p-4 rounded-xl bg-slate-900/20 border border-slate-850 space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-400">Activity Category:</span>
                <span className="font-medium text-slate-200">{record.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Facility / Location ID:</span>
                <span className="font-semibold text-slate-200">{record.facility_id || 'N/A'}</span>
              </div>
              {record.cost_center && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Cost Center Reference:</span>
                  <span className="font-semibold text-slate-200">{record.cost_center}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-slate-400">Transaction Date:</span>
                <span className="font-medium text-slate-200">{record.transaction_date || 'N/A'}</span>
              </div>
              <div className="flex justify-between items-center pt-1 border-t border-slate-800">
                <span className="text-slate-400">Calculated Confidence:</span>
                <span className="font-bold text-brand-400">
                  {Math.round(record.confidence_score * 100)}%
                </span>
              </div>
            </div>

          </div>
        </div>

      </div>

      {/* Validation Checks */}
      <div className="p-6 rounded-2xl glass-panel">
        <h3 className="font-extrabold text-white text-base mb-3 flex items-center gap-2">
          Automatic Validation & Flagging Report
        </h3>
        
        {record.validation_issues.length === 0 ? (
          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-900/60 text-emerald-400 text-xs font-semibold flex items-center gap-2">
            <CheckCircle className="h-4.5 w-4.5" /> All automated validations passed. No warning flags raised.
          </div>
        ) : (
          <div className="space-y-3">
            {record.validation_issues.map((issue) => (
              <div
                key={issue.id}
                className={`p-3.5 rounded-xl border flex items-start gap-3 text-xs ${
                  issue.severity === 'error'
                    ? 'bg-red-950/30 border-red-900/50 text-red-400'
                    : 'bg-amber-950/30 border-amber-900/50 text-amber-400'
                }`}
              >
                <AlertTriangle className="h-4.5 w-4.5 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold uppercase tracking-wider text-[10px]">
                    {issue.issue_type.replace('_', ' ')} • Severity: {issue.severity}
                  </div>
                  <div className="mt-1 font-medium leading-relaxed">{issue.message}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Review Actions Panel */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Sign off actions */}
        <div className="p-6 rounded-2xl glass-panel space-y-4">
          <h3 className="font-extrabold text-white text-base">
            Analyst Review Actions
          </h3>
          
          <div className="space-y-3">
            <label className="block text-xs font-bold uppercase text-slate-400 tracking-wider">
              Analyst Review Comment
            </label>
            <textarea
              disabled={record.locked_for_audit}
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Enter audit notes, check references, or explain changes..."
              className="w-full bg-slate-950 border border-slate-800 focus:border-brand-500 rounded-lg p-3 text-xs text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-brand-500 disabled:opacity-40 min-h-[100px]"
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleApprove}
              disabled={record.locked_for_audit || approveMutation.isLoading}
              className="flex-1 py-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-40 text-white rounded-lg text-xs font-bold transition-all active:scale-[0.98]"
            >
              {approveMutation.isLoading ? 'Processing...' : 'Approve & Lock'}
            </button>
            <button
              onClick={handleReject}
              disabled={record.locked_for_audit || rejectMutation.isLoading}
              className="flex-1 py-2 bg-red-950/40 border border-red-900/60 hover:bg-red-900 hover:text-white disabled:opacity-40 text-red-400 rounded-lg text-xs font-bold transition-all active:scale-[0.98]"
            >
              {rejectMutation.isLoading ? 'Processing...' : 'Reject Row'}
            </button>
            <button
              onClick={handleAddCommentOnly}
              disabled={!commentText.trim() || commentMutation.isLoading}
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-bold transition-all disabled:opacity-40"
            >
              Comment Only
            </button>
          </div>
          
          {record.locked_for_audit && (
            <p className="text-[10px] text-slate-500 leading-relaxed italic">
              * Approved records are sealed as immutable objects and cannot be rejected or modified.
            </p>
          )}
        </div>

        {/* History Timeline */}
        <div className="p-6 rounded-2xl glass-panel flex flex-col">
          <h3 className="font-extrabold text-white text-base mb-4 flex items-center gap-2">
            <History className="h-4.5 w-4.5 text-slate-400" /> Record Activity Trail
          </h3>
          
          <div className="flex-1 space-y-4 overflow-y-auto max-h-[250px] pr-2">
            {record.reviews.length === 0 ? (
              <div className="text-slate-500 italic text-xs py-4 text-center">
                No notes or decisions logged yet.
              </div>
            ) : (
              <div className="relative pl-4 border-l border-slate-850 space-y-5">
                {record.reviews.map((dec) => (
                  <div key={dec.id} className="relative text-xs">
                    {/* Bullet marker */}
                    <div className={`absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full border-2 bg-slate-950 ${
                      dec.action === 'approve' ? 'border-emerald-500' :
                      dec.action === 'reject' ? 'border-red-500' :
                      'border-indigo-400'
                    }`}></div>
                    
                    <div className="flex items-center justify-between text-[10px] text-slate-500">
                      <span className="font-bold text-slate-400 uppercase">
                        {dec.action} • {dec.analyst?.username || 'System'}
                      </span>
                      <span>{new Date(dec.created_at).toLocaleString()}</span>
                    </div>
                    {dec.comment_text && (
                      <div className="mt-1.5 p-2 rounded-lg bg-slate-900/60 text-slate-300 font-medium">
                        {dec.comment_text}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

      </div>

    </div>
  );
}
