import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { History, User, Calendar, Database, CheckSquare, Trash } from 'lucide-react';
import { auditsAPI } from '../api/endpoints';

export default function AuditTrail() {
  const { data: logs = [], isLoading, error } = useQuery({
    queryKey: ['systemAuditTimeline'],
    queryFn: auditsAPI.getSystemTimeline,
    refetchOnWindowFocus: false
  });

  const getActionIcon = (action) => {
    if (action.includes('upload')) return <Database className="h-4 w-4 text-blue-400" />;
    if (action.includes('approve')) return <CheckSquare className="h-4 w-4 text-emerald-400" />;
    if (action.includes('reject')) return <Trash className="h-4 w-4 text-red-400" />;
    return <History className="h-4 w-4 text-indigo-400" />;
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-white">
          System-Wide Audit Trail
        </h1>
        <p className="text-slate-400 mt-1">
          Cryptographically referenced logs detailing all uploads, approvals, and comments.
        </p>
      </div>

      {/* Main Timeline Card */}
      <div className="p-6 rounded-2xl glass-panel relative overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-brand-500"></div>
          </div>
        ) : error ? (
          <div className="text-red-400 text-sm py-4">Error loading audit logs.</div>
        ) : logs.length === 0 ? (
          <div className="text-slate-500 text-sm py-16 text-center border border-dashed border-slate-800 rounded-xl">
            No audit logs have been recorded yet. Ingest and review data to populate the timeline.
          </div>
        ) : (
          <div className="relative pl-6 border-l border-slate-800 space-y-8 py-2">
            {logs.map((log) => (
              <div key={log.id} className="relative group">
                {/* Timeline Bullet node */}
                <div className="absolute -left-[35px] top-1.5 h-7 w-7 rounded-full bg-slate-950 border border-slate-800 flex items-center justify-center shadow-lg group-hover:border-brand-500/50 transition-colors">
                  {getActionIcon(log.action)}
                </div>

                <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
                  <div>
                    <h4 className="text-sm font-extrabold text-white capitalize">
                      {log.action.replace('_', ' ')}
                    </h4>
                    <p className="text-xs text-slate-400 mt-0.5">
                      Target Resource ID: <span className="font-mono">{log.target_id}</span> ({log.target_type})
                    </p>
                  </div>
                  
                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    <span className="flex items-center gap-1">
                      <User className="h-3.5 w-3.5" /> {log.user}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="h-3.5 w-3.5" /> {new Date(log.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                {/* State Diff Details */}
                {(log.before_state || log.after_state) && (
                  <div className="mt-3 p-3 rounded-xl bg-slate-950/60 border border-slate-900 font-mono text-[11px] max-w-2xl overflow-x-auto space-y-1">
                    {log.before_state && (
                      <div className="text-red-400/90 truncate">
                        <span className="font-bold text-red-500">- BEFORE:</span> {JSON.stringify(log.before_state)}
                      </div>
                    )}
                    {log.after_state && (
                      <div className="text-emerald-400/95 truncate">
                        <span className="font-bold text-emerald-500">+ AFTER:</span> {JSON.stringify(log.after_state)}
                      </div>
                    )}
                  </div>
                )}

              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
