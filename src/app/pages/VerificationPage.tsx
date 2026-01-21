import React, { useState } from 'react';
import { Shield, CheckCircle, XCircle, Upload, FileText, Building, Calendar, User } from 'lucide-react';
import { useDiplomas, Diploma } from '@/app/contexts/DiplomaContext';

export const VerificationPage = () => {
  const { verifyDiploma } = useDiplomas();
  const [diplomaFile, setDiplomaFile] = useState<File | null>(null);
  const [verificationResult, setVerificationResult] = useState<{
    valid: boolean;
    diploma?: Diploma;
    error?: string;
  } | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setDiplomaFile(file);
      setVerificationResult(null);
    }
  };

  const handleReset = () => {
    setDiplomaFile(null);
    setVerificationResult(null);
  };

  const handleVerify = async () => {
    if (!diplomaFile) return;

    try {
      const fileContent = await diplomaFile.text();
      const result = await verifyDiploma(fileContent);
      setVerificationResult(result);
    } catch (error) {
      setVerificationResult({
        valid: false,
        error: 'Erreur lors de la lecture du fichier',
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-full mb-4">
            <Shield className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-4xl mb-3">Vérification de Diplôme</h1>
          <p className="text-xl text-gray-600">
            Vérifiez instantanément l'authenticité d'un diplôme numérique
          </p>
        </div>

        {/* Upload Section */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="mb-6">
            <h2 className="text-2xl mb-2">Télécharger le fichier du diplôme</h2>
            <p className="text-gray-600">
              Sélectionnez le fichier JSON du diplôme que vous souhaitez vérifier
            </p>
          </div>

          <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-[#4CAF50] transition-colors">
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <label htmlFor="diploma-file" className="cursor-pointer">
              <span className="text-lg text-gray-700">
                {diplomaFile ? (
                  <span className="flex items-center justify-center gap-2">
                    <FileText className="h-5 w-5 text-[#4CAF50]" />
                    {diplomaFile.name}
                  </span>
                ) : (
                  'Cliquez pour sélectionner un fichier JSON'
                )}
              </span>
              <input
                id="diploma-file"
                type="file"
                accept=".json,application/json"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          </div>

          {diplomaFile && (
            <div className="mt-6">
              <button
                onClick={handleVerify}
                className="w-full bg-[#4CAF50] hover:bg-[#45a049] text-white py-4 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <Shield className="h-5 w-5" />
                Vérifier l'authenticité
              </button>
            </div>
          )}
        </div>

        {/* Verification Result */}
        {verificationResult && (
          <div className={`bg-white rounded-2xl shadow-xl overflow-hidden ${
            verificationResult.valid ? 'border-2 border-green-500' : 'border-2 border-red-500'
          }`}>
            <div className={`px-8 py-6 ${
              verificationResult.valid ? 'bg-green-50' : 'bg-red-50'
            }`}>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {verificationResult.valid ? (
                    <>
                      <CheckCircle className="h-10 w-10 text-green-600" />
                      <div>
                        <h2 className="text-2xl text-green-900">Diplôme Valide ✓</h2>
                        <p className="text-green-700">Ce diplôme est authentique et vérifié</p>
                      </div>
                    </>
                  ) : (
                    <>
                      <XCircle className="h-10 w-10 text-red-600" />
                      <div>
                        <h2 className="text-2xl text-red-900">Diplôme Invalide ✗</h2>
                        <p className="text-red-700">
                          {verificationResult.error || 'Ce diplôme n\'a pas pu être vérifié'}
                        </p>
                      </div>
                    </>
                  )}
                </div>
                <button
                  onClick={handleReset}
                  className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
                >
                  Tester un autre diplôme
                </button>
              </div>
            </div>

            {verificationResult.valid && verificationResult.diploma && (
              <div className="p-8 space-y-6">
                <div>
                  <div className="flex items-center gap-2 text-gray-600 mb-2">
                    <User className="h-5 w-5" />
                    <span className="text-sm">Étudiant</span>
                  </div>
                  <p className="text-xl">{verificationResult.diploma.student_name}</p>
                </div>

                <div>
                  <div className="flex items-center gap-2 text-gray-600 mb-2">
                    <FileText className="h-5 w-5" />
                    <span className="text-sm">Titre du diplôme</span>
                  </div>
                  <p className="text-xl">{verificationResult.diploma.degree_name}</p>
                </div>

                <div>
                  <div className="flex items-center gap-2 text-gray-600 mb-2">

                    <Calendar className="h-5 w-5" />
                    <span className="text-sm">Date d'émission</span>
                  </div>
                  <p className="text-lg">
                    {new Date(verificationResult.diploma.issued_at).toLocaleDateString('fr-FR', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                    })}
                  </p>
                </div>

                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center gap-2 text-gray-600 mb-2">
                    <Shield className="h-5 w-5" />
                    <span className="text-sm">Signature cryptographique</span>
                  </div>
                  <p className="text-xs font-mono bg-gray-100 p-3 rounded break-all">
                    {verificationResult.diploma.signature}
                  </p>
                </div>

                {verificationResult.diploma.revoked && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800">
                      ⚠️ Attention : Ce diplôme a été révoqué
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
