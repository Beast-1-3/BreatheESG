import React, { useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';

export default function Layout() {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  useEffect(() => {
    // If no token found, redirect to login
    if (!token) {
      navigate('/login');
    }
  }, [token, navigate]);

  if (!token) return null;

  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-6 md:p-8 max-w-7xl mx-auto w-full overflow-y-auto max-h-[calc(100vh-4rem)]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
