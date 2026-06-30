import React, { useState } from 'react';
import PrePostPredictor from './pages/PrePost';
import PerformanceAnalyzer from './pages/PostAnalysis';
import './App.css';

export default function App() {
  const [activeTab, setActiveTab] = useState('prepost');

  return (
    <div className="app">
      <header className="header">
        <div className="header-inner">
          <div className="logo">
            <span className="logo-icon"></span>
            <div>
              <h1>Creator Co-Pilot</h1>
              <p>AI-powered Instagram content strategy for nano & micro creators</p>
            </div>
          </div>
          <div className="badges">
            <span className="badge">PySpark</span>
            <span className="badge">XGBoost</span>
            <span className="badge">DistilBERT</span>
            <span className="badge">spaCy</span>
            <span className="badge">Flask</span>
            <span className="badge">React</span>
          </div>
        </div>
      </header>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'prepost' ? 'active' : ''}`}
          onClick={() => setActiveTab('prepost')}
        >
          🔮 Pre-Post Predictor
        </button>
        <button
          className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveTab('performance')}
        >
          📊 Performance Analyzer
        </button>
      </div>

      {activeTab === 'prepost' && <PrePostPredictor />}
      {activeTab === 'performance' && <PerformanceAnalyzer />}

      <footer className="footer">
        Instagram Creator Co-Pilot · PySpark + XGBoost + DistilBERT + spaCy + Flask + React
      </footer>
    </div>
  );
}