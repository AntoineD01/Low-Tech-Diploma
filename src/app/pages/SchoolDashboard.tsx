import React, { useState, useEffect } from 'react';
import { FileText, Download, Calendar, User, Award, AlertCircle, XCircle } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { useDiplomas, Diploma } from '@/app/contexts/DiplomaContext';
import { useNavigate } from 'react-router-dom';

export const SchoolDashboard = () => {
  const { user } = useAuth();
  const { diplomas, revokeDiploma, loadDiplomas } = useDiplomas();
  const navigate = useNavigate();
  const [isRevoking, setIsRevoking] = useState<string | null>(null);

  useEffect(() => {
    if (user?.role !== 'school') {
      navigate('/');
      return;
    }
    
    loadDiplomas();
  }, [user, navigate, loadDiplomas]);

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

  const handleRevokeDiploma = async (diplomaId: string) => {
    if (!confirm('Êtes-vous sûr de vouloir révoquer ce diplôme ? Cette action est irréversible.')) {
      return;
    }

    setIsRevoking(diplomaId);
    try {
      await revokeDiploma(diplomaId);
    } catch (error) {
      alert('Erreur lors de la révocation du diplôme');
    } finally {
      setIsRevoking(null);
    }
  };

  if (user?.role !== 'school') {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl mb-2">Tous les Diplômes</h1>
          <p className="text-xl text-gray-600">
            Gérez tous les diplômes émis par l'établissement
          </p>
        </div>

        {diplomas.length === 0 ? (
          <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
            <Award className="h-16 w-16 text-gray-300 mx-auto mb-4" />
            <h2 className="text-2xl mb-2 text-gray-700">Aucun diplôme trouvé</h2>
            <p className="text-gray-500">
              Aucun diplôme n'a encore été émis. Allez sur la page "Émettre" pour créer votre premier diplôme.
            </p>
          </div>
        ) : (
          <>
            <div className="mb-4 text-gray-600">
              Total : <span className="font-semibold">{diplomas.length}</span> diplôme{diplomas.length > 1 ? 's' : ''}
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {diplomas.map((diploma) => (
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
                      <User className="h-5 w-5 text-gray-400 flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm text-gray-600">Étudiant</p>
                        <p className="text-gray-900">{diploma.student_name}</p>
                        {diploma.student_email && (
                          <p className="text-sm text-gray-500">{diploma.student_email}</p>
                        )}
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

                    <div className="pt-4 space-y-2">
                      <button
                        onClick={() => downloadVerificationFile(diploma)}
                        className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-lg transition-colors"
                      >
                        <Download className="h-4 w-4" />
                        Télécharger le fichier de vérification
                      </button>
                      
                      {!diploma.revoked && (
                        <button
                          onClick={() => handleRevokeDiploma(diploma.id)}
                          disabled={isRevoking === diploma.id}
                          className="w-full flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          <XCircle className="h-4 w-4" />
                          {isRevoking === diploma.id ? 'Révocation...' : 'Révoquer ce diplôme'}
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-xl p-6">
          <div className="flex items-start gap-3">
            <FileText className="h-6 w-6 text-blue-600 flex-shrink-0 mt-1" />
            <div>
              <h3 className="text-lg mb-2 text-blue-900">Gestion des diplômes</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Visualisez tous les diplômes émis par l'établissement</li>
                <li>• Téléchargez les fichiers de vérification pour les partager</li>
                <li>• Révoquez un diplôme en cas de besoin (action irréversible)</li>
                <li>• Les diplômes révoqués ne seront plus valides lors de la vérification</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
