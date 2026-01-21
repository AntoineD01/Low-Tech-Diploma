import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, LogOut } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-[#2c3e50] text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <Shield className="h-8 w-8" />
              <span className="text-xl">DiplomaChain</span>
            </Link>

            <div className="flex items-center gap-6">
              <Link
                to="/"
                className={`hover:text-gray-300 transition-colors ${
                  isActive('/') ? 'border-b-2 border-white pb-1' : ''
                }`}
              >
                Accueil
              </Link>
              <Link
                to="/verify"
                className={`hover:text-gray-300 transition-colors ${
                  isActive('/verify') ? 'border-b-2 border-white pb-1' : ''
                }`}
              >
                Vérifier
              </Link>
              {isAuthenticated && user?.role === 'school' && (
                <>
                  <Link
                    to="/issue"
                    className={`hover:text-gray-300 transition-colors ${
                      isActive('/issue') ? 'border-b-2 border-white pb-1' : ''
                    }`}
                  >
                    Émettre
                  </Link>
                  <Link
                    to="/diplomas"
                    className={`hover:text-gray-300 transition-colors ${
                      isActive('/diplomas') ? 'border-b-2 border-white pb-1' : ''
                    }`}
                  >
                    Diplômes
                  </Link>
                </>
              )}
              {isAuthenticated && user?.role === 'student' && (
                <Link
                  to="/my-diplomas"
                  className={`hover:text-gray-300 transition-colors ${
                    isActive('/my-diplomas') ? 'border-b-2 border-white pb-1' : ''
                  }`}
                >
                  Mes Diplômes
                </Link>
              )}
              
              {isAuthenticated ? (
                <div className="flex items-center gap-4">
                  <span className="text-sm">{user?.name}</span>
                  <button
                    onClick={logout}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-md transition-colors"
                  >
                    <LogOut className="h-4 w-4" />
                    Déconnexion
                  </button>
                </div>
              ) : (
                <Link
                  to="/login"
                  className="px-4 py-2 bg-[#4CAF50] hover:bg-[#45a049] rounded-md transition-colors"
                >
                  Connexion
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main>{children}</main>

      <footer className="bg-[#2c3e50] text-white mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-sm">© 2026 DiplomaChain - Plateforme sécurisée de vérification de diplômes</p>
            <p className="text-xs mt-2 text-gray-400">Utilisant la vérification cryptographique pour garantir l'authenticité</p>
          </div>
        </div>
      </footer>
    </div>
  );
};
