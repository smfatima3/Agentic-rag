import React, { useState, useEffect } from 'react';
import Agent from './components/Agent';
import './App.css';

function App() {
  const [query, setQuery] = useState('');
  const [price, setPrice] = useState('');
  const [userBudget, setUserBudget] = useState('');
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [agentResponses, setAgentResponses] = useState({
    ReviewAnalyzer: { status: 'idle', output: '' },
    ProductResearcher: { status: 'idle', output: '' },
    PriceQuality: { status: 'idle', output: '' },
    BudgetAdvisor: { status: 'idle', output: '' },
  });
  const [recommendation, setRecommendation] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const getRecommendation = () => {
    if (!query || !price || !userBudget || !image) {
      alert('Please fill in all fields and upload an image.');
      return;
    }

    setIsLoading(true);
    setRecommendation('');
    setAgentResponses({
      ReviewAnalyzer: { status: 'thinking', output: '' },
      ProductResearcher: { status: 'idle', output: '' },
      PriceQuality: { status: 'idle', output: '' },
      BudgetAdvisor: { status: 'idle', output: '' },
    });

    const formData = new FormData();
    formData.append('query', query);
    formData.append('price', price);
    formData.append('user_budget', userBudget);
    formData.append('image', image);

    const eventSource = new EventSource(`http://localhost:8000/api/get-recommendation?${new URLSearchParams({query, price, user_budget}).toString()}`);

    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.agent) {
        setAgentResponses((prevResponses) => ({
          ...prevResponses,
          [data.agent]: { status: data.status, output: data.output },
        }));
      }

      if (data.final_recommendation) {
        setRecommendation(data.final_recommendation);
        setIsLoading(false);
        eventSource.close();
      }
    };

    eventSource.onerror = (err) => {
      console.error("EventSource failed:", err);
      setIsLoading(false);
      eventSource.close();
    };
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Shopping Squad</h1>
        <p>Your personal team of AI agents to help you find the perfect product.</p>
      </header>
      <main>
        <div className="input-section">
          <h2>Get a Recommendation</h2>
          <div className="input-form">
            <textarea
              placeholder="Describe what you're looking for..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <div className="price-inputs">
              <input
                type="number"
                placeholder="Product Price ($)"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
              />
              <input
                type="number"
                placeholder="Your Budget ($)"
                value={userBudget}
                onChange={(e) => setUserBudget(e.target.value)}
              />
            </div>
            <div className="image-upload">
              <input type="file" id="imageUpload" onChange={handleImageChange} accept="image/*" />
              <label htmlFor="imageUpload" className="image-upload-label">
                {image ? 'Change Image' : 'Upload Image'}
              </label>
              {imagePreview && <img src={imagePreview} alt="Selected product" className="image-preview" />}
            </div>
            <button onClick={getRecommendation} disabled={isLoading}>
              {isLoading ? 'Analyzing...' : 'Get Recommendation'}
            </button>
          </div>
        </div>
        <div className="agents-section">
          <h2>Agent Status</h2>
          <div className="agents-container">
            <Agent name="Review Analyzer" status={agentResponses.ReviewAnalyzer.status} output={agentResponses.ReviewAnalyzer.output} />
            <Agent name="Product Researcher" status={agentResponses.ProductResearcher.status} output={agentResponses.ProductResearcher.output} />
            <Agent name="Price-Quality Agent" status={agentResponses.PriceQuality.status} output={agentResponses.PriceQuality.output} />
            <Agent name="Budget Advisor" status={agentResponses.BudgetAdvisor.status} output={agentResponses.BudgetAdvisor.output} />
          </div>
        </div>
        {recommendation && (
          <div className="recommendation-section">
            <h2>Final Recommendation</h2>
            <div className="recommendation-card">
              <p>{recommendation}</p>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;