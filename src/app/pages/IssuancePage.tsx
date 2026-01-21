import React, { useState } from 'react';
import { Award, CheckCircle, AlertCircle } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { useDiplomas } from '@/app/contexts/DiplomaContext';
import { useNavigate } from 'react-router-dom';

export const IssuancePage = () => {
  const { user } = useAuth();
  const { issueDiploma } = useDiplomas();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    studentName: '',
    studentEmail: '',
    title: '',
    description: '',
    issueDate: new Date().toISOString().split('T')[0],
  });
  
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  // Redirect if not a school account
  React.useEffect(() => {
    if (user?.role !== 'school') {
      navigate('/');
    }
  }, [user, navigate]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    try {
      issueDiploma({
        ...formData,
        schoolName: user?.name || 'École',
      });
      
      setSuccess(true);
      // Reset form
      setFormData({
        studentName: '',
        studentEmail: '',
        title: '',
        description: '',
        issueDate: new Date().toISOString().split('T')[0],
      });
    } catch (err) {
      setError('Une erreur est survenue lors de l\'émission du diplôme');
    }
  };

  if (user?.role !== 'school') {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          <div className="bg-[#2c3e50] text-white px-8 py-6">
            <div className="flex items-center gap-3">
              <Award className="h-8 w-8" />
              <div>
                <h1 className="text-3xl">Émettre un Diplôme</h1>
                <p className="text-gray-300 mt-1">Créez un diplôme numérique sécurisé</p>
              </div>
            </div>
          </div>

          <div className="p-8">
            {success && (
              <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm text-green-800">
                    <strong>Diplôme émis avec succès !</strong>
                  </p>
                  <p className="text-sm text-green-700 mt-1">
                    Le diplôme a été généré et envoyé à l'étudiant.
                  </p>
                </div>
              </div>
            )}

            {error && (
              <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="studentName" className="block text-sm mb-2 text-gray-700">
                  Nom de l'étudiant *
                </label>
                <input
                  id="studentName"
                  name="studentName"
                  type="text"
                  value={formData.studentName}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CAF50] focus:border-transparent outline-none transition-all"
                  placeholder="Jean Dupont"
                />
              </div>

              <div>
                <label htmlFor="studentEmail" className="block text-sm mb-2 text-gray-700">
                  Email de l'étudiant *
                </label>
                <input
                  id="studentEmail"
                  name="studentEmail"
                  type="email"
                  value={formData.studentEmail}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CAF50] focus:border-transparent outline-none transition-all"
                  placeholder="jean.dupont@example.com"
                />
              </div>

              <div>
                <label htmlFor="title" className="block text-sm mb-2 text-gray-700">
                  Titre du diplôme *
                </label>
                <input
                  id="title"
                  name="title"
                  type="text"
                  value={formData.title}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CAF50] focus:border-transparent outline-none transition-all"
                  placeholder="Master en Informatique"
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm mb-2 text-gray-700">
                  Description *
                </label>
                <textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  required
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CAF50] focus:border-transparent outline-none transition-all resize-none"
                  placeholder="Diplôme de Master en Informatique avec spécialisation en Intelligence Artificielle..."
                />
              </div>

              <div>
                <label htmlFor="issueDate" className="block text-sm mb-2 text-gray-700">
                  Date d'émission *
                </label>
                <input
                  id="issueDate"
                  name="issueDate"
                  type="date"
                  value={formData.issueDate}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#4CAF50] focus:border-transparent outline-none transition-all"
                />
              </div>

              <div className="pt-4">
                <button
                  type="submit"
                  className="w-full bg-[#4CAF50] hover:bg-[#45a049] text-white py-4 rounded-lg transition-colors flex items-center justify-center gap-2"
                >
                  <Award className="h-5 w-5" />
                  Émettre le diplôme
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};
