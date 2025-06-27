// FILE: frontend/src/App.js
// This is the main application component with the new UI and fixed logic.
import React, { useState } from 'react';
import Agent from './components/Agent'; // Correctly imports the separate Agent component

// Helper to initialize agent states
const initialAgentState = {
  LeadAgent: { status: 'inactive', message: '' },
  ProductResearcher: { status: 'inactive', output: '' },
  PriceQualityAgent: { status: 'inactive', output: '' },
  BudgetAdvisor: { status: 'inactive', output: '' },
};

function App() {
  // State for user inputs
  const [query, setQuery] = useState('durable office coffee maker');
  const [price, setPrice] = useState('150');
  const [budget, setUserBudget] = useState('200');
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');

  // State for application status and results
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [agentStates, setAgentStates] = useState(initialAgentState);
  const [finalRecommendation, setFinalRecommendation] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');

  const handleImageChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleGetRecommendation = () => {
    if (!imageFile) {
      alert('Please upload a product image first.');
      return;
    }

    setIsAnalyzing(true);
    setAgentStates(initialAgentState);
    setFinalRecommendation(null);
    setErrorMessage('');

    const formData = new FormData();
    // === THIS IS THE FIX for the 422 Error ===
    formData.append('query', query);
    formData.append('price', price);
    formData.append('budget', budget); // Use 'budget' to match the backend
    formData.append('image_file', imageFile); // Use 'image_file' to match the backend

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
            setAgentStates(prev => {
                const finalState = {...prev};
                Object.keys(finalState).forEach(key => {
                    if (finalState[key].status === 'thinking') {
                        finalState[key].status = 'complete';
                    }
                });
                return finalState;
            });
            return;
          }
          
          const chunk = decoder.decode(value, { stream: true });
          const events = chunk.split('\n\n').filter(Boolean);

          events.forEach(eventString => {
            // Find the event type line and the data line
            const eventLine = eventString.split('\n').find(line => line.startsWith('event: '));
            const dataLine = eventString.split('\n').find(line => line.startsWith('data: '));

            if (eventLine && dataLine) {
                const eventType = eventLine.substring(7).trim();
                const eventData = dataLine.substring(5).trim();
                
                try {
                    const data = JSON.parse(eventData);
                    
                    if(eventType === 'context_update') {
                        // Update individual agent states based on context
                        Object.keys(data.agent_outputs).forEach(agentName => {
                            setAgentStates(prev => ({
                                ...prev,
                                [agentName]: {
                                    status: 'thinking',
                                    output: data.agent_outputs[agentName].message || JSON.stringify(data.agent_outputs[agentName].data)
                                }
                            }));
                        });
                    } else if (eventType === 'final_recommendation') {
                        setFinalRecommendation(data);
                    } else if (eventType === 'error') {
                        setErrorMessage(data.message || 'An unknown error occurred.');
                        setIsAnalyzing(false);
                    }

                } catch (e) {
                    console.error('Failed to parse JSON from stream:', eventData, e);
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
      setErrorMessage(`Network or server error: ${error.message}`);
      setIsAnalyzing(false);
    });
  };

  return (
    <div className="min-h-screen bg-[#FFFBF5] font-sans text-gray-800">
      <header className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto py-5 px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl font-bold leading-tight text-[#0A2540]">
            AI Shopping Squad
          </h1>
          <p className="text-gray-500 mt-1">Your personal team of AI agents for smarter product research.</p>
        </div>
      </header>
      
      <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* --- LEFT COLUMN: THE BRIEFING --- */}
          <div className="lg:col-span-1">
            <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200">
              <h2 className="text-2xl font-semibold mb-5 text-[#0A2540]">Your Product Briefing</h2>
              <form id="analysis-form" className="space-y-6">
                <div>
                  <label htmlFor="query" className="block text-sm font-medium text-gray-600 mb-1">Product Query</label>
                  <input type="text" id="query" value={query} onChange={e => setQuery(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-orange-500 focus:border-orange-500" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="price" className="block text-sm font-medium text-gray-600 mb-1">Listed Price ($)</label>
                    <input type="number" id="price" value={price} onChange={e => setPrice(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-orange-500 focus:border-orange-500" />
                  </div>
                  <div>
                    <label htmlFor="userBudget" className="block text-sm font-medium text-gray-600 mb-1">Your Budget ($)</label>
                    <input type="number" id="userBudget" value={budget} onChange={e => setUserBudget(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-orange-500 focus:border-orange-500" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Product Image</label>
                  <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
                    <div className="space-y-1 text-center">
                      <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true"><path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
                      <div className="flex text-sm text-gray-600">
                        <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-orange-600 hover:text-orange-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-orange-500">
                          <span>Upload a file</span>
                          <input id="file-upload" name="file-upload" type="file" className="sr-only" onChange={handleImageChange} accept="image/*" />
                        </label>
                        <p className="pl-1">or drag and drop</p>
                      </div>
                      <p className="text-xs text-gray-500">PNG, JPG, GIF up to 10MB</p>
                    </div>
                  </div>
                  {imagePreview && <img src={imagePreview} alt="Preview" className="mt-4 rounded-lg shadow-md w-full h-auto object-cover" />}
                </div>
                <button type="button" onClick={handleGetRecommendation} disabled={isAnalyzing} className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-lg font-medium text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors">
                  {isAnalyzing ? 'Analyzing...' : 'Assemble the Squad'}
                </button>
              </form>
            </div>
          </div>

          {/* --- RIGHT COLUMN: THE ANALYSIS PANEL --- */}
          <div className="lg:col-span-2 space-y-8">
            <div>
              <h2 className="text-2xl font-semibold mb-5 text-[#0A2540]">Agent Roundtable</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Agent name="Lead Agent" status={isAnalyzing ? 'thinking' : 'inactive'} output={agentStates.LeadAgent.message} />
                <Agent name="Product Researcher" status={agentStates.ProductResearcher.status} output={agentStates.ProductResearcher.output} />
                <Agent name="Price-Quality Agent" status={agentStates.PriceQualityAgent.status} output={agentStates.PriceQualityAgent.output} />
                <Agent name="Budget Advisor" status={agentStates.BudgetAdvisor.status} output={agentStates.BudgetAdvisor.output} />
              </div>
            </div>

            {finalRecommendation && !isAnalyzing && (
              <div className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 animate-fade-in">
                <h2 className="text-2xl font-semibold text-[#0A2540] mb-4">Final Recommendation: <span className="text-orange-600">{finalRecommendation.title}</span></h2>
                <div className="space-y-4 text-gray-700">
                    <p><strong>Visual Summary:</strong> {finalRecommendation.visual_summary}</p>
                    <p><strong>Value Assessment:</strong> {finalRecommendation.value_assessment}</p>
                    <p><strong>Budget Advice:</strong> {finalRecommendation.budget_advice}</p>
                </div>
              </div>
            )}

            {errorMessage && (
                <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded-md shadow-lg" role="alert">
                    <p className="font-bold">An Error Occurred</p>
                    <p>{errorMessage}</p>
                </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
