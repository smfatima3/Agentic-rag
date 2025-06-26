// FILE: frontend/src/App.js
// ACTION: This is your main frontend application file.
// It includes the UI, state management, and SSE logic.

import React, { useState, useEffect } from 'react';
import Agent from './components/Agent';

// Helper to initialize agent states
const initialAgentState = {
  ReviewAnalyzer: { status: 'inactive', output: '' },
  ProductResearcher: { status: 'inactive', output: '' },
  PriceQuality: { status: 'inactive', output: '' },
  BudgetAdvisor: { status: 'inactive', output: '' },
};

function App() {
  // State for user inputs
  const [query, setQuery] = useState('durable office coffee maker');
  const [price, setPrice] = useState('150');
  const [userBudget, setUserBudget] = useState('200');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');

  // State for application status and results
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [agentStates, setAgentStates] = useState(initialAgentState);
  const [finalRecommendation, setFinalRecommendation] = useState(null);

  // Handle image selection
  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  // Main function to start the analysis
  const handleGetRecommendation = () => {
    if (!imageFile) {
      alert('Please upload an image first.');
      return;
    }

    // Reset states
    setIsAnalyzing(true);
    setAgentStates(initialAgentState);
    setFinalRecommendation(null);
    
    // This fetch-based streaming implementation is more robust than EventSource for POST requests.
    const formData = new FormData();
    formData.append('query', query);
    formData.append('price', price);
    formData.append('user_budget', userBudget);
    formData.append('image', imageFile);

    // --- THIS IS THE CHANGE ---
    // Use a relative path so it calls the same server that serves the page.
    fetch('/research-product/', { // <-- THIS IS THE ONLY CHANGE
     method: 'POST',
     body: formData,
   })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        function push() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    setIsAnalyzing(false);
                    console.log('Stream complete.');
                    return;
                }
                
                // The value is a Uint8Array, decode it to text
                const chunk = decoder.decode(value, { stream: true });
                
                // SSE messages are separated by \n\n
                const events = chunk.split('\n\n').filter(Boolean);
                
                events.forEach(event => {
                    if (event.startsWith('data:')) {
                        const jsonData = event.substring(5).trim();
                        try {
                            const data = JSON.parse(jsonData);
                            
                            if (data.agent === 'LeadAgent' && data.status === 'complete') {
                                setFinalRecommendation(data.output);
                                setIsAnalyzing(false);
                            } else if (data.agent) { // Ensure agent key exists
                                setAgentStates(prev => ({
                                    ...prev,
                                    [data.agent]: { status: data.status, output: data.output || '' }
                                }));
                            }
                        } catch (e) {
                            console.error('Failed to parse JSON from stream:', jsonData, e);
                        }
                    }
                });
                
                push();
            });
        }
        push();
    })
    .catch(error => {
        console.error('Error fetching recommendation stream:', error);
        setIsAnalyzing(false);
        alert('An error occurred. Check the console for details.');
    });
  };

  return (
    <div className="min-h-screen bg-gray-100 font-sans">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold leading-tight text-gray-900">AI Shopping Squad</h1>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* --- LEFT COLUMN: THE BRIEFING --- */}
          <div className="lg:col-span-1">
            <div className="bg-white p-6 rounded-lg shadow">
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Your Product Briefing</h2>
              <form id="analysis-form" className="space-y-4">
                {/* ... (Your input fields for query, price, budget go here) ... */}
                <div>
                  <label className="block text-sm font-medium text-gray-700">Product Image</label>
                  {/* ... (Your image upload input goes here) ... */}
                  {imagePreview && <img src={imagePreview} alt="Preview" className="mt-2 rounded-lg shadow-md w-full h-auto" />}
                </div>
                <button type="button" onClick={handleGetRecommendation} disabled={isAnalyzing} className="w-full ...">
                  {isAnalyzing ? 'Analyzing...' : 'Assemble the Squad'}
                </button>
              </form>
            </div>
          </div>

          {/* --- RIGHT COLUMN: THE ANALYSIS PANEL --- */}
          <div className="lg:col-span-2 space-y-8">
            {/* Agent Roundtable */}
            <div>
              <h2 className="text-xl font-semibold mb-4 text-gray-800">Agent Analysis</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Agent name="Review Analyzer" status={agentStates.ReviewAnalyzer.status} output={agentStates.ReviewAnalyzer.output} />
                <Agent name="Visual Analyst" status={agentStates.ProductResearcher.status} output={agentStates.ProductResearcher.output} />
                <Agent name="Price & Quality" status={agentStates.PriceQuality.status} output={agentStates.PriceQuality.output} />
                <Agent name="Budget Advisor" status={agentStates.BudgetAdvisor.status} output={agentStates.BudgetAdvisor.output} />
              </div>
            </div>

            {/* Final Recommendation Report */}
            {finalRecommendation && !isAnalyzing && (
              <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold text-gray-800 mb-4">Final Recommendation: {finalRecommendation.title}</h2>
                {/* ... (Display the final pros, cons, and summary here) ... */}
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
