import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [uploadedImage, setUploadedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [nearbyServices, setNearbyServices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [userLocation, setUserLocation] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Get user location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        (error) => {
          console.log('Location access denied');
        }
      );
    }
  }, []);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setUploadedImage(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const analyzeImage = async () => {
    if (!uploadedImage) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', uploadedImage);

    try {
      const response = await fetch(`${API_BASE}/api/analyze-image`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const result = await response.json();
      setAnalysis(result.analysis);
      setCurrentView('analysis');
    } catch (error) {
      console.error('Error analyzing image:', error);
      alert('Failed to analyze image. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const findNearbyServices = async () => {
    setLoading(true);
    try {
      // Use mock location if geolocation is unavailable
      const location = userLocation || { latitude: 40.7128, longitude: -74.0060 };
      
      const response = await fetch(`${API_BASE}/api/find-nearby`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          latitude: location.latitude,
          longitude: location.longitude,
          problem_type: analysis.professional_type
        })
      });

      if (!response.ok) {
        throw new Error('Failed to find services');
      }

      const result = await response.json();
      setNearbyServices(result.services);
      setCurrentView('services');
    } catch (error) {
      console.error('Error finding services:', error);
      alert('Failed to find nearby services. Please try again.');
    } finally {
      setLoading(false);
    }
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
              <path d="M15 45 Q30 35 45 45" stroke="white" strokeWidth="2" fill="none"/>
            </svg>
          </div>
          <h1>Joatx</h1>
          <p>AI-powered household repair assistant</p>
        </div>
        
        <div className="welcome-message">
          <h2>Snap, analyze, repair!</h2>
          <p>Upload a photo of your household problem and get instant AI-powered repair guidance</p>
        </div>
      </div>

      <div className="upload-section">
        <div className="upload-container">
          <h3>🔧 Got a household problem?</h3>
          <p>Take a photo and let our AI analyze it for you</p>
          
          <div className="upload-area">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="file-input"
              id="image-upload"
            />
            <label htmlFor="image-upload" className="upload-button">
              📸 Upload Photo
            </label>
          </div>

          {imagePreview && (
            <div className="image-preview">
              <img src={imagePreview} alt="Uploaded" className="preview-image" />
              <button 
                onClick={analyzeImage} 
                disabled={loading}
                className="analyze-button"
              >
                {loading ? 'Analyzing...' : '🤖 Analyze with AI'}
              </button>
            </div>
          )}
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🔍</div>
            <h4>AI Image Analysis</h4>
            <p>Advanced AI identifies your household problems from photos</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🛠️</div>
            <h4>Step-by-Step Guides</h4>
            <p>Get personalized repair instructions based on your specific issue</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📍</div>
            <h4>Find Local Help</h4>
            <p>Locate nearby stores, electricians, and repair professionals</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h4>Emergency Contacts</h4>
            <p>Quick access to emergency repair services when you need them</p>
          </div>
        </div>
      </div>
    </div>
  );

  const AnalysisView = () => (
    <div className="analysis-view">
      <div className="analysis-header">
        <button className="back-button" onClick={() => setCurrentView('home')}>
          ← Back to Home
        </button>
        <h2>AI Analysis Results</h2>
      </div>

      {analysis && (
        <div className="analysis-content">
          <div className="problem-summary">
            <div className="problem-card">
              <h3>🔍 Problem Identified</h3>
              <p className="problem-text">{analysis.problem_identified}</p>
              <div className="problem-meta">
                <span className={`difficulty ${analysis.difficulty_level.toLowerCase()}`}>
                  {analysis.difficulty_level}
                </span>
                <span className="repair-type">{analysis.repair_type}</span>
              </div>
            </div>

            <div className="quick-info">
              <div className="info-grid">
                <div className="info-item">
                  <span className="icon">⏱️</span>
                  <div>
                    <strong>Time</strong>
                    <p>{analysis.estimated_time}</p>
                  </div>
                </div>
                <div className="info-item">
                  <span className="icon">💰</span>
                  <div>
                    <strong>Cost</strong>
                    <p>{analysis.estimated_cost}</p>
                  </div>
                </div>
                <div className="info-item">
                  <span className="icon">👨‍🔧</span>
                  <div>
                    <strong>Can DIY?</strong>
                    <p>{analysis.can_diy ? 'Yes' : 'Call Professional'}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="analysis-details">
            <div className="safety-section">
              <h3>⚠️ Safety Warnings</h3>
              <ul className="safety-list">
                {analysis.safety_warnings.map((warning, index) => (
                  <li key={index} className="safety-item">{warning}</li>
                ))}
              </ul>
            </div>

            <div className="tools-materials">
              <div className="section">
                <h3>🛠️ Tools Needed</h3>
                <ul>
                  {analysis.tools_needed.map((tool, index) => (
                    <li key={index}>{tool}</li>
                  ))}
                </ul>
              </div>

              <div className="section">
                <h3>📦 Materials Needed</h3>
                <ul>
                  {analysis.materials_needed.map((material, index) => (
                    <li key={index}>{material}</li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="repair-steps">
              <h3>🔧 Repair Steps</h3>
              <div className="steps-container">
                {analysis.steps.map((step, index) => (
                  <div key={index} className={`step-card ${step.safety_critical ? 'safety-critical' : ''}`}>
                    <div className="step-number">{step.step}</div>
                    <div className="step-content">
                      <h4>{step.title}</h4>
                      <p>{step.description}</p>
                      {step.safety_critical && (
                        <div className="safety-badge">⚠️ Safety Critical</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="action-buttons">
              {analysis.professional_needed ? (
                <button className="action-button professional" onClick={findNearbyServices}>
                  🏠 Find Local Professionals
                </button>
              ) : (
                <button className="action-button supplies" onClick={findNearbyServices}>
                  🏪 Find Nearby Stores
                </button>
              )}
              <button className="action-button emergency" onClick={() => setCurrentView('emergency')}>
                🚨 Emergency Contact
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const ServicesView = () => (
    <div className="services-view">
      <div className="services-header">
        <button className="back-button" onClick={() => setCurrentView('analysis')}>
          ← Back to Analysis
        </button>
        <h2>Nearby Services</h2>
      </div>

      <div className="services-content">
        {nearbyServices.length === 0 ? (
          <div className="loading">Finding nearby services...</div>
        ) : (
          <div className="services-grid">
            {nearbyServices.map((service, index) => (
              <div key={index} className="service-card">
                <div className="service-header">
                  <h3>{service.name}</h3>
                  <div className="service-rating">
                    <span className="rating">⭐ {service.rating}</span>
                    <span className="distance">📍 {service.distance}</span>
                  </div>
                </div>
                
                <div className="service-details">
                  <p className="address">📍 {service.address}</p>
                  <p className="phone">📞 {service.phone}</p>
                  <div className="specialties">
                    <strong>Specialties:</strong>
                    <div className="specialty-tags">
                      {service.specialties.map((specialty, idx) => (
                        <span key={idx} className="specialty-tag">{specialty}</span>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="service-actions">
                  <button className="action-button call" onClick={() => window.location.href = `tel:${service.phone}`}>
                    📞 Call Now
                  </button>
                  <button className="action-button directions" onClick={() => window.open(`https://maps.google.com/?q=${encodeURIComponent(service.address)}`, '_blank')}>
                    🗺️ Get Directions
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  const EmergencyView = () => (
    <div className="emergency-view">
      <div className="emergency-header">
        <button className="back-button" onClick={() => setCurrentView('analysis')}>
          ← Back to Analysis
        </button>
        <h2>🚨 Emergency Services</h2>
      </div>

      <div className="emergency-content">
        <div className="emergency-warning">
          <h3>⚠️ Safety First</h3>
          <p>If you're experiencing a gas leak, electrical fire, or major water leak, evacuate immediately and call emergency services!</p>
        </div>

        <div className="emergency-contacts">
          <div className="contact-card urgent">
            <h3>🚨 Immediate Emergency</h3>
            <p>Fire, Gas Leak, Electrical Hazard</p>
            <button className="emergency-button" onClick={() => window.location.href = 'tel:911'}>
              Call 911
            </button>
          </div>

          <div className="contact-card">
            <h3>⚡ Emergency Electrician</h3>
            <p>24/7 Electrical Emergency Service</p>
            <button className="emergency-button" onClick={() => window.location.href = 'tel:555-ELECTRIC'}>
              Call (555) ELECTRIC
            </button>
          </div>

          <div className="contact-card">
            <h3>🚰 Emergency Plumber</h3>
            <p>24/7 Plumbing Emergency Service</p>
            <button className="emergency-button" onClick={() => window.location.href = 'tel:555-PLUMBER'}>
              Call (555) PLUMBER
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="App">
      {currentView === 'home' && <HomeView />}
      {currentView === 'analysis' && <AnalysisView />}
      {currentView === 'services' && <ServicesView />}
      {currentView === 'emergency' && <EmergencyView />}
    </div>
  );
}

export default App;