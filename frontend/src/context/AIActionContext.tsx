import React, { createContext, useState, useContext, ReactNode } from 'react';
import { AIParsedDetails } from '../types';

interface AIActionContextType {
  suggestion: AIParsedDetails | null;
  setSuggestion: (suggestion: AIParsedDetails | null) => void;
}

const AIActionContext = createContext<AIActionContextType | undefined>(undefined);

export const AIActionProvider = ({ children }: { children: ReactNode }) => {
  const [suggestion, setSuggestion] = useState<AIParsedDetails | null>(null);

  return (
    <AIActionContext.Provider value={{ suggestion, setSuggestion }}>
      {children}
    </AIActionContext.Provider>
  );
};

export const useAIAction = () => {
  const context = useContext(AIActionContext);
  if (context === undefined) {
    throw new Error('useAIAction must be used within an AIActionProvider');
  }
  return context;
};
