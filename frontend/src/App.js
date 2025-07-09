import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [guides, setGuides] = useState([]);
  const [currentGuide, setCurrentGuide] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [userId] = useState(() => localStorage.getItem('userId') || 'user_' + Date.now());
  const [loading, setLoading] = useState(false);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    localStorage.setItem('userId', userId);
    fetchGuides();
  }, [userId]);

  const fetchGuides = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/guides`);
      const data = await response.json();
      setGuides(data);
    } catch (error) {
      console.error('Error fetching guides:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchGuide = async (guideId) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/guides/${guideId}`);
      const guide = await response.json();
      setCurrentGuide(guide);
      
      // Fetch user progress
      const progressResponse = await fetch(`${API_BASE}/api/progress/${userId}/${guideId}`);
      const progress = await progressResponse.json();
      setCurrentStep(progress.current_step || 0);
    } catch (error) {
      console.error('Error fetching guide:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateProgress = async (step) => {
    try {
      await fetch(`${API_BASE}/api/progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          guide_id: currentGuide.id,
          current_step: step,
          completed: step >= currentGuide.steps.length
        }),
      });
    } catch (error) {
      console.error('Error updating progress:', error);
    }
  };

  const nextStep = () => {
    if (currentStep < currentGuide.steps.length - 1) {
      const newStep = currentStep + 1;
      setCurrentStep(newStep);
      updateProgress(newStep);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      const newStep = currentStep - 1;
      setCurrentStep(newStep);
      updateProgress(newStep);
    }
  };

  const startGuide = (guide) => {
    fetchGuide(guide.id);
    setCurrentView('guide');
  };

  const HomeView = () => (
    <div className="home-view">
      <div className="hero-section">
        <div className="logo-container">
          <div className="logo">
            <svg width="60" height="60" viewBox="0 0 60 60">
              <circle cx="30" cy="30" r="25" fill="#3B82F6" stroke="#1E40AF" strokeWidth="2"/>
              <path d="M20 30 L25 35 L40 20" stroke="white" strokeWidth="3" fill="none"/>
              <circle cx="30" cy="15" r="3" fill="#FCD34D"/>
              <rect x="28" y="18" width="4" height="8" fill="#FCD34D"/>
            </svg>
          </div>
          <h1>Joatx</h1>
          <p>Your household repair companion</p>
        </div>
        
        <div className="welcome-message">
          <h2>Simple repairs, step by step</h2>
          <p>Get clear instructions for common household repairs</p>
        </div>
      </div>

      <div className="guides-section">
        <h3>Available Guides</h3>
        {loading ? (
          <div className="loading">Loading guides...</div>
        ) : (
          <div className="guides-grid">
            {guides.map(guide => (
              <div key={guide.id} className="guide-card" onClick={() => startGuide(guide)}>
                <div className="guide-header">
                  <h4>{guide.title}</h4>
                  <span className={`difficulty ${guide.difficulty.toLowerCase()}`}>
                    {guide.difficulty}
                  </span>
                </div>
                <div className="guide-info">
                  <div className="info-item">
                    <span className="icon">⏱️</span>
                    <span>{guide.estimated_time}</span>
                  </div>
                  <div className="info-item">
                    <span className="icon">💰</span>
                    <span>{guide.estimated_cost}</span>
                  </div>
                  <div className="info-item">
                    <span className="icon">🔧</span>
                    <span>{guide.tools_needed.length} tools</span>
                  </div>
                </div>
                <button className="start-button">Start Guide</button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const GuideView = () => {
    if (!currentGuide) return <div>Loading...</div>;

    const currentStepData = currentGuide.steps[currentStep];
    const progress = ((currentStep + 1) / currentGuide.steps.length) * 100;

    return (
      <div className="guide-view">
        <div className="guide-header">
          <button className="back-button" onClick={() => setCurrentView('home')}>
            ← Back to Home
          </button>
          <h2>{currentGuide.title}</h2>
          <div className="progress-bar">
            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
          </div>
          <span className="progress-text">
            Step {currentStep + 1} of {currentGuide.steps.length}
          </span>
        </div>

        {currentView === 'guide' && (
          <div className="guide-content">
            <div className="step-content">
              <h3>{currentStepData.title}</h3>
              
              {currentStepData.safety_warning && (
                <div className="safety-warning">
                  <span className="icon">⚠️</span>
                  <strong>Safety Warning:</strong> {currentStepData.safety_warning}
                </div>
              )}

              {currentStepData.image_url && (
                <img 
                  src={currentStepData.image_url} 
                  alt={currentStepData.title}
                  className="step-image"
                />
              )}

              <p className="step-description">{currentStepData.description}</p>

              <div className="step-navigation">
                <button 
                  className="nav-button prev" 
                  onClick={prevStep}
                  disabled={currentStep === 0}
                >
                  ← Previous
                </button>
                <button 
                  className="nav-button next" 
                  onClick={nextStep}
                  disabled={currentStep === currentGuide.steps.length - 1}
                >
                  Next →
                </button>
              </div>
            </div>

            <div className="guide-sidebar">
              <div className="section">
                <h4>🛠️ Tools Needed</h4>
                <ul>
                  {currentGuide.tools_needed.map((tool, index) => (
                    <li key={index}>{tool}</li>
                  ))}
                </ul>
              </div>

              <div className="section">
                <h4>📦 Materials</h4>
                <ul>
                  {currentGuide.materials_needed.map((material, index) => (
                    <li key={index}>{material}</li>
                  ))}
                </ul>
              </div>

              <div className="section">
                <h4>⚠️ Safety Tips</h4>
                <ul>
                  {currentGuide.safety_tips.map((tip, index) => (
                    <li key={index}>{tip}</li>
                  ))}
                </ul>
              </div>

              <div className="section">
                <h4>📊 Quick Info</h4>
                <div className="quick-info">
                  <div className="info-item">
                    <span>⏱️ Time:</span>
                    <span>{currentGuide.estimated_time}</span>
                  </div>
                  <div className="info-item">
                    <span>💰 Cost:</span>
                    <span>{currentGuide.estimated_cost}</span>
                  </div>
                  <div className="info-item">
                    <span>🎯 Difficulty:</span>
                    <span className={`difficulty ${currentGuide.difficulty.toLowerCase()}`}>
                      {currentGuide.difficulty}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentStep === currentGuide.steps.length - 1 && (
          <div className="completion-message">
            <h3>🎉 Great Job!</h3>
            <p>You've completed the {currentGuide.title} repair guide!</p>
            <button className="complete-button" onClick={() => setCurrentView('home')}>
              Back to Home
            </button>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="App">
      {currentView === 'home' && <HomeView />}
      {currentView === 'guide' && <GuideView />}
    </div>
  );
}

export default App;