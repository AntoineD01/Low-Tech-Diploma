import React, { useState } from 'react';
import { Award, CheckCircle, AlertCircle, Upload, FileSpreadsheet, Download } from 'lucide-react';
import { useAuth } from '@/app/contexts/AuthContext';
import { useDiplomas } from '@/app/contexts/DiplomaContext';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '@/config';

type TabType = 'single' | 'bulk';

interface BulkResult {
  total: number;
  success: number;
  failed: number;
  details: Array<{
    student: string;
    status: string;
    diploma_id?: string;
    email_sent?: boolean;
    error?: string;
  }>;
}

export const IssuancePage = () => {
  const { user } = useAuth();
  const { issueDiploma } = useDiplomas();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState<TabType>('single');
  const [formData, setFormData] = useState({
    studentName: '',
    studentEmail: '',
    title: '',
    description: '',
    issueDate: new Date().toISOString().split('T')[0],
  });
  
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  
  // Bulk import state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [bulkLoading, setBulkLoading] = useState(false);
  const [bulkResult, setBulkResult] = useState<BulkResult | null>(null);

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    try {
      await issueDiploma({
        studentName: formData.studentName,
        studentEmail: formData.studentEmail,
        title: formData.title,
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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setBulkResult(null);
      setError('');
    }
  };

  const handleBulkUpload = async () => {
    if (!selectedFile) {
      setError('Veuillez sélectionner un fichier');
      return;
    }

    setBulkLoading(true);
    setError('');
    setBulkResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/bulk_issue`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Erreur lors de l\'import');
      }

      const result = await response.json();
      setBulkResult(result);
      setSelectedFile(null);
      
      // Reset file input
      const fileInput = document.getElementById('bulk-file-input') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
      
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors de l\'import en masse');
    } finally {
      setBulkLoading(false);
    }
  };

  const downloadTemplate = () => {
    const csvContent = "student_name,student_email,degree_name\nJean Dupont,jean.dupont@example.com,Master en Informatique\nMarie Martin,marie.martin@example.com,Licence en Mathématiques";
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'template_diplomes.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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
                <p className="text-gray-300 mt-1">Créez des diplômes numériques sécurisés</p>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => {
                  setActiveTab('single');
                  setError('');
                  setSuccess(false);
                  setBulkResult(null);
                }}
                className={`flex-1 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'single'
                    ? 'border-[#4CAF50] text-[#4CAF50]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <Award className="h-4 w-4" />
                  Émission individuelle
                </div>
              </button>
              <button
                onClick={() => {
                  setActiveTab('bulk');
                  setError('');
                  setSuccess(false);
                }}
                className={`flex-1 px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === 'bulk'
                    ? 'border-[#4CAF50] text-[#4CAF50]'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <FileSpreadsheet className="h-4 w-4" />
                  Import en masse
                </div>
              </button>
            </div>
          </div>

          <div className="p-8">
            {/* Single diploma form */}
            {activeTab === 'single' && (
              <>
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
            </>
            )}

            {/* Bulk import */}
            {activeTab === 'bulk' && (
              <div className="space-y-6">
                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                    <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                )}

                {bulkResult && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h3 className="font-semibold text-blue-900 mb-3">Résultat de l'import</h3>
                    <div className="grid grid-cols-3 gap-4 mb-4">
                      <div className="bg-white rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-gray-700">{bulkResult.total}</div>
                        <div className="text-xs text-gray-600">Total</div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-green-700">{bulkResult.success}</div>
                        <div className="text-xs text-green-600">Réussis</div>
                      </div>
                      <div className="bg-red-50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-red-700">{bulkResult.failed}</div>
                        <div className="text-xs text-red-600">Échoués</div>
                      </div>
                    </div>
                    
                    {bulkResult.details.length > 0 && (
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-700 mb-2">Détails :</h4>
                        <div className="max-h-60 overflow-y-auto space-y-2">
                          {bulkResult.details.map((detail, idx) => (
                            <div
                              key={idx}
                              className={`text-sm p-2 rounded ${
                                detail.status === 'success'
                                  ? 'bg-green-50 text-green-800'
                                  : 'bg-red-50 text-red-800'
                              }`}
                            >
                              <div className="flex items-start justify-between">
                                <span className="font-medium">{detail.student}</span>
                                <span className="text-xs">
                                  {detail.status === 'success' ? '✓' : '✗'}
                                </span>
                              </div>
                              {detail.error && (
                                <div className="text-xs mt-1 text-red-600">{detail.error}</div>
                              )}
                              {detail.email_sent !== undefined && (
                                <div className="text-xs mt-1">
                                  Email: {detail.email_sent ? '✓ envoyé' : '✗ non envoyé'}
                                </div>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-semibold text-blue-900 mb-2">Format du fichier</h3>
                  <p className="text-sm text-blue-800 mb-3">
                    Le fichier doit être au format CSV ou Excel (.xlsx, .xls) avec les colonnes suivantes :
                  </p>
                  <ul className="text-sm text-blue-800 space-y-1 mb-3 list-disc list-inside">
                    <li><code className="bg-blue-100 px-1 rounded">student_name</code> - Nom de l'étudiant</li>
                    <li><code className="bg-blue-100 px-1 rounded">student_email</code> - Email de l'étudiant</li>
                    <li><code className="bg-blue-100 px-1 rounded">degree_name</code> - Nom du diplôme</li>
                  </ul>
                  <button
                    onClick={downloadTemplate}
                    className="text-sm text-blue-700 hover:text-blue-900 font-medium flex items-center gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Télécharger un modèle
                  </button>
                </div>

                <div>
                  <label className="block text-sm mb-2 text-gray-700 font-medium">
                    Sélectionner un fichier
                  </label>
                  <div className="flex items-center gap-3">
                    <input
                      id="bulk-file-input"
                      type="file"
                      accept=".csv,.xlsx,.xls"
                      onChange={handleFileChange}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-gray-100 file:text-gray-700 hover:file:bg-gray-200 transition-colors"
                    />
                  </div>
                  {selectedFile && (
                    <p className="mt-2 text-sm text-gray-600">
                      Fichier sélectionné : <strong>{selectedFile.name}</strong>
                    </p>
                  )}
                </div>

                <button
                  onClick={handleBulkUpload}
                  disabled={!selectedFile || bulkLoading}
                  className="w-full bg-[#4CAF50] hover:bg-[#45a049] text-white py-4 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  {bulkLoading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      Import en cours...
                    </>
                  ) : (
                    <>
                      <Upload className="h-5 w-5" />
                      Importer les diplômes
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
