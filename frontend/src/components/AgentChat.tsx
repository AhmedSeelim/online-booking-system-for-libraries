import React, { useState, useRef, useEffect } from 'react';
import { sendMessage } from '../api/ai';
import { useAuth } from '../context/AuthContext';
import { useAIAction } from '../context/AIActionContext';
import { AIParsedDetails } from '../types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { me } from '../api/auth';

interface Message {
  sender: 'user' | 'ai';
  text?: string;
  data?: any;
}

const AgentChat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { currentUser, setCurrentUser } = useAuth();
  const { setSuggestion } = useAIAction();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, isLoading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendMessage({ text: input });
      const aiMessage: Message = { sender: 'ai', data: response };
      setMessages(prev => [...prev, aiMessage]);

      // More robustly check if the AI's response indicates a successful transaction, then refetch the user to update the balance.
      const responseText = (response.response || '').toLowerCase();
      const transactionKeywords = [
        'purchase successful',
        'booking confirmed',
        'has been charged',
        'has been deducted',
        'remaining balance'
      ];

      if (transactionKeywords.some(keyword => responseText.includes(keyword))) {
        try {
          const updatedUser = await me();
          setCurrentUser(updatedUser);
        } catch (error) {
          console.error("Failed to refetch user after AI transaction:", error);
        }
      }


      if(response.parsed_details && Object.keys(response.parsed_details).length > 0) {
        setSuggestion(response.parsed_details);
      } else {
        setSuggestion(null);
      }

    } catch (error) {
      console.error("Failed to send message", error);
      const errorMessage: Message = { sender: 'ai', text: "Sorry, I encountered an error." };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSuggestion = (details: AIParsedDetails) => {
    setSuggestion(details);
    const suggestionAppliedMessage: Message = { sender: 'ai', text: "I've pre-filled the form with the details. Please review and confirm." };
    setMessages(prev => [...prev, suggestionAppliedMessage]);
  };

  const renderAiMessage = (data: any) => {
    // Renders a list of items from the AI's "result" field.
    const ResultList = ({ items }: { items: any[] }) => (
      <ul className="list-disc list-inside mt-2 space-y-2 text-sm">
        {items.map((item: any, i: number) => (
          <li key={i}>
            {/* Book item */}
            {item.title && <strong>{item.title}</strong>}
            {item.author && ` by ${item.author}`}
            {item.price != null && ` - $${item.price.toFixed(2)}`}
            {/* Resource item */}
            {item.name && <strong>{item.name}</strong>}
            {item.type && ` (${item.type})`}
            {item.hourly_rate != null && ` - $${item.hourly_rate.toFixed(2)}/hr`}
          </li>
        ))}
      </ul>
    );

    const hasResponseText = typeof data.response === 'string' && data.response.trim();
    const hasResultList = Array.isArray(data.result) && data.result.length > 0;

    return (
       <div>
        {/* Main conversational text from the agent */}
        {hasResponseText && (
          <div className="markdown-content">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.response}</ReactMarkdown>
          </div>
        )}

        {/* Structured list data from a tool call */}
        {hasResultList && <ResultList items={data.result} />}

        {/* Fallback message if neither response nor result is available */}
        {!hasResponseText && !hasResultList && (
          <p>I'm sorry, I couldn't find any specific information for that.</p>
        )}

        {/* Clarification question from the agent */}
        {data.clarify && <p className="mt-3 italic text-gray-500 dark:text-gray-400">"{data.clarify}"</p>}
        
        {/* Suggestion button if there are parsed details */}
        {data.parsed_details && Object.keys(data.parsed_details).length > 0 && (
          <button onClick={() => handleSuggestion(data.parsed_details)} className="mt-3 w-full bg-green-500 hover:bg-green-600 text-white text-sm font-bold py-1 px-2 rounded">
            Apply Suggestion
          </button>
        )}
        
        {/* Metadata footer */}
        <div className="text-xs text-gray-400 dark:text-gray-500 mt-3 pt-2 border-t border-gray-300 dark:border-gray-600 flex justify-between font-mono">
            <span>{data.intent}</span>
            <span>Audit: {data.audit_id}</span>
        </div>
      </div>
    )
  }

  if (!currentUser) {
    return (
      <div className="flex flex-col h-full p-4 items-center justify-center text-center">
        <h3 className="text-lg font-semibold">AI Assistant</h3>
        <p className="text-sm text-gray-500">Please log in to use the AI assistant.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <header className="p-4 border-b border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold">AI Assistant</h3>
      </header>
      <div className="flex-1 p-4 overflow-y-auto bg-gray-50 dark:bg-gray-800">
        {messages.map((msg, index) => (
          <div key={index} className={`mb-4 flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`rounded-lg px-4 py-2 max-w-sm shadow ${msg.sender === 'user' ? 'bg-indigo-500 text-white' : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'}`}>
              {msg.text}
              {msg.data && renderAiMessage(msg.data)}
            </div>
          </div>
        ))}
        {isLoading && (
            <div className="mb-4 flex justify-start">
                <div className="rounded-lg px-4 py-3 max-w-xs shadow bg-white dark:bg-gray-700">
                    <div className="flex items-center justify-center space-x-1.5">
                        <div className="typing-dot typing-dot-1"></div>
                        <div className="typing-dot typing-dot-2"></div>
                        <div className="typing-dot typing-dot-3"></div>
                    </div>
                </div>
            </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSend} className="p-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything..."
            className="flex-1 p-2 border rounded-l-md focus:ring-indigo-500 focus:border-indigo-500 bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600"
            disabled={isLoading}
          />
          <button type="submit" className="px-4 py-2 bg-indigo-600 text-white rounded-r-md hover:bg-indigo-700 disabled:bg-indigo-300" disabled={isLoading}>
            Send
          </button>
        </div>
      </form>
    </div>
  );
};

export default AgentChat;