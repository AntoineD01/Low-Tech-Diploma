import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, AlertCircle } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const success = await login(email, password);
      if (success) {
        // Redirect based on role
        if (email.includes('school')) {
          navigate('/issue');
        } else {
          navigate('/my-diplomas');
        }
      } else {
        setError('Email ou mot de passe incorrect');
      }
    } catch (err) {
      setError('Une erreur est survenue lors de la connexion');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-[#2c3e50] rounded-full mb-4">
              <Shield className="h-8 w-8 text-white" />
            </div>
            <h2 className="text-3xl">Connexion</h2>
            <p className="text-gray-600 mt-2">Accédez à votre espace sécurisé</p>
          </div>

          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm mb-2 text-gray-700">
                Adresse email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CAF50] focus:border-transparent outline-none transition-all"
                placeholder="vous@example.com"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm mb-2 text-gray-700">
                Mot de passe
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CAF50] focus:border-transparent outline-none transition-all"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#4CAF50] hover:bg-[#45a049] text-white py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Connexion en cours...' : 'Se connecter'}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center">
              <strong>Comptes de démonstration :</strong>
            </p>
            <div className="mt-3 space-y-2 text-sm text-gray-600">
              <p>📚 École : <code className="bg-gray-100 px-2 py-1 rounded">school@example.com</code></p>
              <p>🎓 Étudiant : <code className="bg-gray-100 px-2 py-1 rounded">student@example.com</code></p>
              <p className="text-center mt-2">Mot de passe : <code className="bg-gray-100 px-2 py-1 rounded">password123</code></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
