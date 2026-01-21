import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from '@/app/contexts/AuthContext';
import { DiplomaProvider } from '@/app/contexts/DiplomaContext';
import { Layout } from '@/app/components/Layout';
import { HomePage } from '@/app/pages/HomePage';
import { LoginPage } from '@/app/pages/LoginPage';
import { IssuancePage } from '@/app/pages/IssuancePage';
import { VerificationPage } from '@/app/pages/VerificationPage';
import { StudentDashboard } from '@/app/pages/StudentDashboard';

export default function App() {
  return (
    <AuthProvider>
      <DiplomaProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/verify" element={<VerificationPage />} />
            <Route path="/issue" element={<IssuancePage />} />
            <Route path="/my-diplomas" element={<StudentDashboard />} />
          </Routes>
        </Layout>
      </DiplomaProvider>
    </AuthProvider>
  );
}
