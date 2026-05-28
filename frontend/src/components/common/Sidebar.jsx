import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, UploadCloud, ShieldAlert, History } from 'lucide-react';

export default function Sidebar() {
  const links = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/uploads', label: 'Upload Center', icon: UploadCloud },
    { to: '/review', label: 'Analyst Review', icon: ShieldAlert },
    { to: '/audit-trail', label: 'Audit Log', icon: History }
  ];

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950/80 p-4 flex flex-col justify-between min-h-[calc(100vh-4rem)]">
      <nav className="space-y-1.5">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-200 group ${
                  isActive
                    ? 'bg-brand-900/40 text-brand-400 border-l-4 border-brand-500 shadow-lg shadow-brand-950/20'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-900'
                }`
              }
            >
              <Icon className="h-5 w-5 text-slate-400 group-[.active]:text-brand-400 transition-colors" />
              {link.label}
            </NavLink>
          );
        })}
      </nav>
      
      <div className="p-4 rounded-xl bg-gradient-to-br from-slate-900 to-brand-950/20 border border-slate-800/80">
        <h4 className="text-xs font-bold uppercase text-brand-400 tracking-wider mb-1">
          Auditor Mode Enabled
        </h4>
        <p className="text-xs text-slate-400 leading-relaxed">
          Approved records are cryptographically sealed & locked for reporting.
        </p>
      </div>
    </aside>
  );
}
