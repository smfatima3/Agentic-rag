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
    fetch('/api/get-recommendation', {
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
    <div className="min-h-screen bg-gray-50 font-sans p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">AI Shopping Squad</h1>
          <p className="text-lg text-gray-600 mt-2">Upload a product image and your preferences to get a collaborative AI-powered recommendation.</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Column: Inputs */}
          <div className="lg:col-span-1 bg-white p-6 rounded-xl shadow-md border border-gray-200">
            <h2 className="text-2xl font-semibold mb-4">Your Preferences</h2>
            <form id="analysis-form">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Query</label>
                  <input type="text" value={query} onChange={e => setQuery(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                </div>
                <div className="flex space-x-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Product Price ($)</label>
                    <input type="number" value={price} onChange={e => setPrice(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Your Budget ($)</label>
                    <input type="number" value={userBudget} onChange={e => setUserBudget(e.target.value)} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Product Image</label>
                  <div className="mt-1 flex items-center space-x-4">
                     {imagePreview && <img src={imagePreview} alt="Preview" className="h-16 w-16 rounded-md object-cover" />}
                     <input type="file" onChange={handleImageChange} accept="image/*" className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-600 hover:file:bg-indigo-100"/>
                  </div>
                </div>
              </div>
              <button type="button" onClick={handleGetRecommendation} disabled={isAnalyzing} className="mt-6 w-full inline-flex justify-center py-3 px-4 border border-transparent shadow-sm text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400">
                {isAnalyzing ? 'Analyzing...' : 'Get Recommendation'}
              </button>
            </form>
          </div>

          {/* Right Column: Agents & Results */}
          <div className="lg:col-span-2">
             <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Agent name="Review Analyzer" status={agentStates.ReviewAnalyzer.status} output={agentStates.ReviewAnalyzer.output} />
                <Agent name="Product Researcher" status={agentStates.ProductResearcher.status} output={agentStates.ProductResearcher.output} />
                <Agent name="Price-Quality Agent" status={agentStates.PriceQuality.status} output={agentStates.PriceQuality.output} />
                <Agent name="Budget Advisor" status={agentStates.BudgetAdvisor.status} output={agentStates.BudgetAdvisor.output} />
            </div>
            {finalRecommendation && !isAnalyzing && (
                <div className="mt-8 bg-white p-6 rounded-xl shadow-lg border border-gray-200">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Final Recommendation: {finalRecommendation.title}</h2>
                    <div className="space-y-4 text-gray-700">
                        <div>
                            <h3 className="font-semibold">Visual Summary:</h3>
                            <p>{finalRecommendation.visual_summary}</p>
                        </div>
                        <div>
                            <h3 className="font-semibold">Value Assessment:</h3>
                            <p>{finalRecommendation.value_assessment}</p>
                        </div>
                         <div>
                            <h3 className="font-semibold">Budget Advice:</h3>
                            <p>{finalRecommendation.budget_advice}</p>
                        </div>
                    </div>
                </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
