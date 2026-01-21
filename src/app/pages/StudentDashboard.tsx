import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, Building, Award, AlertCircle } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { useDiplomas, Diploma } from '@/app/contexts/DiplomaContext';
import { useNavigate } from 'react-router-dom';

export const StudentDashboard = () => {
  const { user } = useAuth();
  const { getUserDiplomas } = useDiplomas();
  const navigate = useNavigate();
  const [userDiplomas, setUserDiplomas] = useState<Diploma[]>([]);

  useEffect(() => {
    if (user?.role !== 'student') {
      navigate('/');
      return;
    }
    
    if (user?.username) {
      const diplomas = getUserDiplomas(user.username);
      setUserDiplomas(diplomas);
    }
  }, [user, getUserDiplomas, navigate]);

  const downloadDiploma = async (diploma: Diploma) => {
    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || ''}/download_pdf/${diploma.id}`, {
        headers: {
          'Authorization': token,
        },
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `diplome_${diploma.student_name}_${diploma.id}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Failed to download diploma:', error);
    }
  };

  const downloadVerificationFile = (diploma: Diploma) => {
    const verificationData = {
      id: diploma.id,
      student_name: diploma.student_name,
      degree_name: diploma.degree_name,
      issued_at: diploma.issued_at,
      signature: diploma.signature,
      revoked: diploma.revoked
    };
    
    const dataStr = JSON.stringify(verificationData, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `verification_${diploma.student_name}_${diploma.id}.json`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (user?.role !== 'student') {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2">Mes Diplômes</h1>
          <p className="text-xl text-gray-600">
            Gérez et téléchargez vos diplômes numériques
          </p>
        </div>

        {userDiplomas.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <Award className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl mb-2 text-gray-700">Aucun diplôme trouvé</h2>
            <p className="text-gray-500">
              Vous n'avez pas encore de diplômes émis. Vos diplômes apparaîtront ici une fois qu'ils seront émis par votre établissement.
            </p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {userDiplomas.map((diploma) => (
              <div
                key={diploma.id}
                className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
              >
                <div className="bg-gradient-to-br from-[#2c3e50] to-[#34495e] p-6 text-white">
                  <div className="flex items-start justify-between mb-3">
                    <Award className="h-8 w-8" />
                    {diploma.revoked && (
                      <span className="bg-red-500 text-xs px-2 py-1 rounded">
                        Révoqué
                      </span>
                    )}
                  </div>
                  <h3 className="text-xl mb-2">{diploma.degree_name}</h3>
                  <p className="text-sm text-gray-300 line-clamp-2">Diplôme certifié</p>
                </div>

                <div className="p-6 space-y-4">
                  <div className="flex items-start gap-3">
                    <Building className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-600">Étudiant</p>
                      <p className="text-gray-900">{diploma.student_name}</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <Calendar className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-600">Date d'émission</p>
                      <p className="text-gray-900">
                        {new Date(diploma.issued_at).toLocaleDateString('fr-FR', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })}
                      </p>
                    </div>
                  </div>

                  {diploma.revoked && (
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
                      <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                      <p className="text-sm text-red-800">
                        Ce diplôme a été révoqué et n'est plus valide
                      </p>
                    </div>
                  )}

                  <div className="pt-4">
                    <button
                      onClick={() => downloadDiploma(diploma)}
                      className="w-full flex items-center justify-center gap-2 bg-[#4CAF50] hover:bg-[#45a049] text-white py-3 rounded-lg transition-colors mb-2"
                    >
                      <Download className="h-4 w-4" />
                      Télécharger le PDF
                    </button>
                    <button
                      onClick={() => downloadVerificationFile(diploma)}
                      className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg transition-colors"
                    >
                      <FileText className="h-4 w-4" />
                      Télécharger le fichier de vérification
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {userDiplomas.length > 0 && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
            <div className="flex items-start gap-3">
              <FileText className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="text-lg mb-2 text-blue-900">Comment utiliser vos diplômes ?</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Téléchargez le <strong>fichier de vérification JSON</strong> de votre diplôme</li>
                  <li>• Partagez-le avec les employeurs ou institutions qui en ont besoin</li>
                  <li>• Ils pourront vérifier son authenticité sur la page de vérification</li>
                  <li>• Le fichier PDF est pour votre usage personnel, le fichier JSON est pour la vérification</li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
