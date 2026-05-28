import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/common/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import UploadCenter from './pages/UploadCenter';
import ReviewDashboard from './pages/ReviewDashboard';
import RecordDetail from './pages/RecordDetail';
import AuditTrail from './pages/AuditTrail';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Public Auth Routes */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected App Routes */}
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="uploads" element={<UploadCenter />} />
            <Route path="review" element={<ReviewDashboard />} />
            <Route path="records/:id" element={<RecordDetail />} />
            <Route path="audit-trail" element={<AuditTrail />} />
          </Route>

          {/* Catch-all Redirect */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
