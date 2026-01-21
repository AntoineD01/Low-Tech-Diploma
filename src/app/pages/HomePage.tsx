import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, FileCheck, Award, CheckCircle, Lock, Database } from 'lucide-react';

export const HomePage = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-[#2c3e50] to-[#34495e] text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-5xl mb-6">
              Plateforme Sécurisée de Diplômes Numériques
            </h1>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Vérifiez l'authenticité de vos diplômes grâce à la vérification cryptographique.
              Une solution moderne et sécurisée pour les établissements d'enseignement et les étudiants.
            </p>
            <div className="mt-10 flex gap-4 justify-center">
              <Link
                to="/verify"
                className="px-8 py-4 bg-[#4CAF50] hover:bg-[#45a049] rounded-lg text-lg transition-colors flex items-center gap-2"
              >
                <FileCheck className="h-5 w-5" />
                Vérifier un diplôme
              </Link>
              <Link
                to="/login"
                className="px-8 py-4 bg-white text-[#2c3e50] hover:bg-gray-100 rounded-lg text-lg transition-colors"
              >
                Connexion
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Cards */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            {/* Issue Diplomas Card */}
            <div className="bg-white border-2 border-gray-200 rounded-xl p-8 hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-[#4CAF50] rounded-full flex items-center justify-center mb-6">
                <Award className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl mb-4">Émettre des Diplômes</h3>
              <p className="text-gray-600 mb-6">
                Pour les établissements scolaires : émettez des diplômes numériques sécurisés avec
                vérification cryptographique intégrée.
              </p>
              <Link
                to="/login"
                className="inline-block px-6 py-3 bg-[#4CAF50] text-white rounded-lg hover:bg-[#45a049] transition-colors"
              >
                Accéder à l'émission
              </Link>
            </div>

            {/* Verify Authenticity Card */}
            <div className="bg-white border-2 border-gray-200 rounded-xl p-8 hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mb-6">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl mb-4">Vérifier l'Authenticité</h3>
              <p className="text-gray-600 mb-6">
                Pour tout le monde : vérifiez instantanément l'authenticité d'un diplôme numérique
                en téléchargeant le fichier JSON.
              </p>
              <Link
                to="/verify"
                className="inline-block px-6 py-3 bg-[#4CAF50] text-white rounded-lg hover:bg-[#45a049] transition-colors"
              >
                Vérifier maintenant
              </Link>
            </div>

            {/* Manage Diplomas Card */}
            <div className="bg-white border-2 border-gray-200 rounded-xl p-8 hover:shadow-xl transition-shadow">
              <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mb-6">
                <FileCheck className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-2xl mb-4">Gérer Vos Diplômes</h3>
              <p className="text-gray-600 mb-6">
                Pour les étudiants : accédez à tous vos diplômes numériques en un seul endroit,
                téléchargez-les et partagez-les facilement.
              </p>
              <Link
                to="/login"
                className="inline-block px-6 py-3 bg-[#4CAF50] text-white rounded-lg hover:bg-[#45a049] transition-colors"
              >
                Voir mes diplômes
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Security Features */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl mb-4">Sécurité et Confiance</h2>
            <p className="text-xl text-gray-600">
              Notre plateforme utilise des technologies de pointe pour garantir la sécurité de vos diplômes
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="flex flex-col items-center text-center">
              <Lock className="h-12 w-12 text-[#4CAF50] mb-4" />
              <h3 className="text-xl mb-2">Cryptographie Avancée</h3>
              <p className="text-gray-600">
                Chaque diplôme est protégé par un hash cryptographique unique garantissant son intégrité
              </p>
            </div>
            <div className="flex flex-col items-center text-center">
              <Database className="h-12 w-12 text-[#4CAF50] mb-4" />
              <h3 className="text-xl mb-2">Base de Données Sécurisée</h3>
              <p className="text-gray-600">
                Stockage sécurisé de tous les diplômes avec accès contrôlé et traçabilité complète
              </p>
            </div>
            <div className="flex flex-col items-center text-center">
              <CheckCircle className="h-12 w-12 text-[#4CAF50] mb-4" />
              <h3 className="text-xl mb-2">Vérification Instantanée</h3>
              <p className="text-gray-600">
                Vérifiez l'authenticité d'un diplôme en quelques secondes avec notre système de validation
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
