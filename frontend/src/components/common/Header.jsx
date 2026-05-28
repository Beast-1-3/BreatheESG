import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, User, Leaf } from 'lucide-react';

export default function Header() {
  const navigate = useNavigate();
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/60 px-6 flex items-center justify-between sticky top-0 z-10 backdrop-blur-md">
      <div className="flex items-center gap-2">
        <Leaf className="h-6 w-6 text-brand-500 animate-pulse" />
        <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-brand-400 bg-clip-text text-transparent">
          Breathe <span className="text-brand-500">ESG</span>
        </span>
        <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
          Ops Platform
        </span>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/40 border border-slate-800">
          <User className="h-4 w-4 text-brand-400" />
          <div className="text-sm font-medium text-slate-300">
            {user.username} <span className="text-xs text-slate-500">({user.email})</span>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="p-2 text-slate-400 hover:text-red-400 hover:bg-slate-800/60 rounded-lg transition-all"
          title="Log Out"
        >
          <LogOut className="h-4.5 w-4.5" />
        </button>
      </div>
    </header>
  );
}
