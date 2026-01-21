import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface Diploma {
  id: string;
  studentName: string;
  studentEmail: string;
  title: string;
  description: string;
  issueDate: string;
  schoolName: string;
  hash: string;
  revoked: boolean;
}

interface DiplomaContextType {
  diplomas: Diploma[];
  issueDiploma: (diploma: Omit<Diploma, 'id' | 'hash' | 'revoked'>) => string;
  verifyDiploma: (diplomaData: string) => { valid: boolean; diploma?: Diploma; error?: string };
  getUserDiplomas: (email: string) => Diploma[];
  revokeDiploma: (id: string) => void;
}

const DiplomaContext = createContext<DiplomaContextType | undefined>(undefined);

// Simple hash function for demo purposes
const simpleHash = async (data: string): Promise<string> => {
  const encoder = new TextEncoder();
  const dataBuffer = encoder.encode(data);
  
  try {
    const hashBuffer = await crypto.subtle.digest('SHA-256', dataBuffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  } catch {
    // Fallback for environments without crypto.subtle
    let hash = 0;
    for (let i = 0; i < data.length; i++) {
      const char = data.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash;
    }
    return Math.abs(hash).toString(16).padStart(64, '0');
  }
};

export const DiplomaProvider = ({ children }: { children: ReactNode }) => {
  const [diplomas, setDiplomas] = useState<Diploma[]>([]);

  useEffect(() => {
    // Load diplomas from localStorage
    const saved = localStorage.getItem('diplomas');
    if (saved) {
      setDiplomas(JSON.parse(saved));
    }
  }, []);

  useEffect(() => {
    // Save diplomas to localStorage
    localStorage.setItem('diplomas', JSON.stringify(diplomas));
  }, [diplomas]);

  const issueDiploma = (diplomaData: Omit<Diploma, 'id' | 'hash' | 'revoked'>): string => {
    const id = Math.random().toString(36).substr(2, 9);
    const dataToHash = JSON.stringify({ ...diplomaData, id });
    
    simpleHash(dataToHash).then(hash => {
      const newDiploma: Diploma = {
        ...diplomaData,
        id,
        hash,
        revoked: false,
      };
      
      setDiplomas(prev => [...prev, newDiploma]);
    });
    
    return id;
  };

  const verifyDiploma = (diplomaData: string): { valid: boolean; diploma?: Diploma; error?: string } => {
    try {
      const parsedDiploma = JSON.parse(diplomaData) as Diploma;
      
      // Check if diploma exists in our database
      const storedDiploma = diplomas.find(d => d.id === parsedDiploma.id);
      
      if (!storedDiploma) {
        return { valid: false, error: 'Diplôme non trouvé dans la base de données' };
      }
      
      // Check if revoked
      if (storedDiploma.revoked) {
        return { valid: false, diploma: storedDiploma, error: 'Ce diplôme a été révoqué' };
      }
      
      // Verify hash matches
      if (storedDiploma.hash !== parsedDiploma.hash) {
        return { valid: false, error: 'Le hash du diplôme ne correspond pas' };
      }
      
      return { valid: true, diploma: storedDiploma };
    } catch (error) {
      return { valid: false, error: 'Format de diplôme invalide' };
    }
  };

  const getUserDiplomas = (email: string): Diploma[] => {
    return diplomas.filter(d => d.studentEmail === email);
  };

  const revokeDiploma = (id: string) => {
    setDiplomas(prev => prev.map(d => 
      d.id === id ? { ...d, revoked: true } : d
    ));
  };

  return (
    <DiplomaContext.Provider value={{ diplomas, issueDiploma, verifyDiploma, getUserDiplomas, revokeDiploma }}>
      {children}
    </DiplomaContext.Provider>
  );
};

export const useDiplomas = () => {
  const context = useContext(DiplomaContext);
  if (context === undefined) {
    throw new Error('useDiplomas must be used within a DiplomaProvider');
  }
  return context;
};
