import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { API_BASE_URL } from '@/config';

export interface Diploma {
  id: string;
  student_name: string;
  student_email?: string;
  degree_name: string;
  issued_at: string;
  signature: string;
  revoked: boolean;
}

interface DiplomaContextType {
  diplomas: Diploma[];
  issueDiploma: (data: { studentName: string; studentEmail: string; title: string }) => Promise<string>;
  verifyDiploma: (diplomaData: string) => Promise<{ valid: boolean; diploma?: Diploma; error?: string }>;
  getUserDiplomas: (username: string) => Diploma[];
  revokeDiploma: (id: string) => Promise<void>;
  loadDiplomas: () => Promise<void>;
}

const DiplomaContext = createContext<DiplomaContextType | undefined>(undefined);

export const DiplomaProvider = ({ children }: { children: ReactNode }) => {
  const [diplomas, setDiplomas] = useState<Diploma[]>([]);
  const [token, setToken] = useState<string>('');

  const getToken = () => {
    return localStorage.getItem('token') || '';
  };

  // Monitor token changes
  useEffect(() => {
    const currentToken = getToken();
    setToken(currentToken);
  }, []);

  // Also check for token changes periodically or on storage events
  useEffect(() => {
    const handleStorageChange = () => {
      const currentToken = getToken();
      setToken(currentToken);
    };

    window.addEventListener('storage', handleStorageChange);
    
    // Also check on focus (when user comes back to tab)
    window.addEventListener('focus', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('focus', handleStorageChange);
    };
  }, []);

  const loadDiplomas = async () => {
    const currentToken = getToken();
    if (!currentToken) {
      setDiplomas([]);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/list`, {
        headers: {
          'Authorization': currentToken,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDiplomas(data);
      } else {
        setDiplomas([]);
      }
    } catch (error) {
      console.error('Failed to load diplomas:', error);
      setDiplomas([]);
    }
  };

  useEffect(() => {
    loadDiplomas();
  }, [token]);

  const issueDiploma = async (data: { studentName: string; studentEmail: string; title: string }): Promise<string> => {
    const token = getToken();
    
    try {
      const response = await fetch(`${API_BASE_URL}/issue`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token,
        },
        body: JSON.stringify({
          student_name: data.studentName,
          student_email: data.studentEmail,
          degree_name: data.title,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        // Reload diplomas to get the new one
        await loadDiplomas();
        return result.diploma_id;
      } else {
        throw new Error('Failed to issue diploma');
      }
    } catch (error) {
      console.error('Failed to issue diploma:', error);
      throw error;
    }
  };

  const verifyDiploma = async (diplomaData: string): Promise<{ valid: boolean; diploma?: Diploma; error?: string }> => {
    try {
      const parsedDiploma = JSON.parse(diplomaData);
      
      const response = await fetch(`${API_BASE_URL}/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parsedDiploma),
      });

      if (response.ok) {
        const result = await response.json();
        return {
          valid: result.valid,
          diploma: parsedDiploma,
          error: result.reason,
        };
      } else {
        return { valid: false, error: 'Failed to verify diploma' };
      }
    } catch (error) {
      return { valid: false, error: 'Invalid diploma format' };
    }
  };

  const getUserDiplomas = (username: string): Diploma[] => {
    return diplomas.filter((d: any) => 
      d.student_name === username || 
      d.student_email === username ||
      d.student_name?.toLowerCase() === username.toLowerCase() ||
      d.student_email?.toLowerCase() === username.toLowerCase()
    );
  };

  const revokeDiploma = async (id: string): Promise<void> => {
    const token = getToken();
    
    try {
      const response = await fetch(`${API_BASE_URL}/revoke`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': token,
        },
        body: JSON.stringify({ id }),
      });

      if (response.ok) {
        await loadDiplomas();
      }
    } catch (error) {
      console.error('Failed to revoke diploma:', error);
      throw error;
    }
  };

  return (
    <DiplomaContext.Provider value={{ diplomas, issueDiploma, verifyDiploma, getUserDiplomas, revokeDiploma, loadDiplomas }}>
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
