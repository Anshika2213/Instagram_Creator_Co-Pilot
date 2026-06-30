import React, { useState } from 'react';
import axios from 'axios';

const CATEGORIES = [
  'Beauty','Comedy','Fashion','Fitness','Food',
  'Lifestyle','Music','Photography','Technology','Travel'
];

export default function CaptionAnalyzer() {
  const [caption, setCaption] = useState('');
  const [hashtags, setHashtags] = useState('');
  const [category, setCategory] = useState('Fitness');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyze = async () => {
    if (!caption.trim()) {
      setError('Please enter a caption to analyze');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const hashtagList = hashtags
        .split(/[\s,]+/)
        .filter(h => h.trim())
        .map(h => h.startsWith('#') ? h : `#${h}`);

      const res = await axios.post(
        'http://localhost:5000/analyze-caption',
        { caption, hashtags: hashtagList, category }
      );
      setResult(res.data);
    } catch (err) {
      setError('Could not connect to backend. Make sure Flask is running.');
    }
    setLoading(false);
  };

  const gradeColor = {
    A: '#6bcb77', B: '#fcb045',
    C: '#4d96ff', D: '#ff9f43', F: '#ff6b6b'
  };

  const sentimentColor = {
    Positive: '#6bcb77', Neutral: '#4d96ff', Negative: '#ff6b6b'
  };

  return (
    <div>
      {/* Description */}
      <div className="card" style={{ borderLeft: '3px solid #6bcb77' }}>
        <p style={{ color: '#888', fontSize: '0.9rem', lineHeight: 1.6 }}>
          <strong style={{ color: '#ccc' }}>NLP Caption Analyzer</strong><br />
          Paste your Instagram caption and hashtags. The NLP module automatically
          detects sentiment using DistilBERT, scores caption quality across 7 dimensions
          using spaCy, and checks hashtag relevance against your niche.
        </p>
      </div>

      {/* Form */}
      <div className="card">
        <div className="card-title">Caption Input</div>

        <div className="form-group full" style={{ marginBottom: 16 }}>
          <label>Your Caption</label>
          <textarea
            value={caption}
            onChange={e => setCaption(e.target.value)}
            placeholder="Paste your Instagram caption here..."
            rows={5}
            style={{
              background: '#111',
              border: '1px solid #2a2a2a',
              borderRadius: 8,
              padding: '12px 14px',
              color: '#f0f0f0',
              fontSize: '0.92rem',
              outline: 'none',
              resize: 'vertical',
              fontFamily: 'inherit',
              lineHeight: 1.6
            }}
          />
          <div style={{ color: '#444', fontSize: '0.75rem', marginTop: 4 }}>
            {caption.length} characters · {caption.split(/\s+/).filter(w => w).length} words
          </div>
        </div>

        <div className="form-grid" style={{ marginBottom: 16 }}>
          <div className="form-group">
            <label>Content Category</label>
            <select value={category} onChange={e => setCategory(e.target.value)}>
              {CATEGORIES.map(c => <option key={c}>{c}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Hashtags (space or comma separated)</label>
            <input
              type="text"
              value={hashtags}
              onChange={e => setHashtags(e.target.value)}
              placeholder="#fitness #workout #gym"
            />
          </div>
        </div>

        <button className="btn" onClick={analyze} disabled={loading}>
          {loading ? '⏳ Analyzing...' : '🔍 Analyze Caption'}
        </button>
      </div>

      {/* Error */}
      {error && <div className="error-box">⚠️ {error}</div>}

      {/* Loading */}
      {loading && (
        <div className="loading">
          Running DistilBERT sentiment analysis + spaCy quality scoring...
        </div>
      )}

      {/* Results */}
      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Row 1: Sentiment + Score side by side */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>

            {/* Sentiment */}
            <div className="card" style={{
              borderTop: `3px solid ${sentimentColor[result.sentiment?.label] || '#555'}`
            }}>
              <div className="card-title">🤖 Sentiment (DistilBERT)</div>
              <div style={{ textAlign: 'center', padding: '12px 0' }}>
                <div style={{
                  fontSize: '2rem',
                  fontWeight: 800,
                  color: sentimentColor[result.sentiment?.label] || '#fff'
                }}>
                  {result.sentiment?.label}
                </div>
                <div style={{ color: '#555', fontSize: '0.85rem', marginTop: 6 }}>
                  {result.sentiment?.confidence}% confidence
                </div>
                <div style={{
                  marginTop: 12,
                  background: '#111',
                  borderRadius: 8,
                  padding: '8px 12px',
                  fontSize: '0.8rem',
                  color: '#666'
                }}>
                  Detected by DistilBERT NLP model
                </div>
              </div>
            </div>

            {/* Caption Score */}
            <div className="card" style={{
              borderTop: `3px solid ${gradeColor[result.caption_quality?.grade] || '#555'}`
            }}>
              <div className="card-title">📝 Caption Quality Score</div>
              <div style={{ textAlign: 'center', padding: '8px 0' }}>
                <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'baseline', gap: 8 }}>
                  <div style={{
                    fontSize: '3rem',
                    fontWeight: 900,
                    color: gradeColor[result.caption_quality?.grade] || '#fff'
                  }}>
                    {result.caption_quality?.score}
                  </div>
                  <div style={{ color: '#444', fontSize: '1.2rem' }}>
                    /{result.caption_quality?.max_score}
                  </div>
                </div>
                <div style={{
                  display: 'inline-block',
                  padding: '4px 16px',
                  borderRadius: 20,
                  background: gradeColor[result.caption_quality?.grade] || '#555',
                  color: '#000',
                  fontWeight: 800,
                  fontSize: '1rem',
                  marginTop: 6
                }}>
                  Grade: {result.caption_quality?.grade}
                </div>
                <div style={{ marginTop: 12, display: 'flex', justifyContent: 'center', gap: 16 }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ color: '#fff', fontWeight: 600 }}>
                      {result.caption_quality?.word_count}
                    </div>
                    <div style={{ color: '#555', fontSize: '0.72rem' }}>words</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ color: '#fff', fontWeight: 600 }}>
                      {result.caption_quality?.emoji_count}
                    </div>
                    <div style={{ color: '#555', fontSize: '0.72rem' }}>emojis</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ color: result.caption_quality?.has_question ? '#6bcb77' : '#ff6b6b', fontWeight: 600 }}>
                      {result.caption_quality?.has_question ? '✓' : '✗'}
                    </div>
                    <div style={{ color: '#555', fontSize: '0.72rem' }}>question</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ color: result.caption_quality?.has_cta ? '#6bcb77' : '#ff6b6b', fontWeight: 600 }}>
                      {result.caption_quality?.has_cta ? '✓' : '✗'}
                    </div>
                    <div style={{ color: '#555', fontSize: '0.72rem' }}>CTA</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Row 2: Positives + Issues */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {/* Positives */}
            {result.caption_quality?.positives?.length > 0 && (
              <div className="card">
                <div className="card-title">✅ What's Working</div>
                <ul className="suggestions">
                  {result.caption_quality.positives.map((p, i) => (
                    <li key={i} style={{ borderLeft: '3px solid #6bcb77' }}>{p}</li>
                  ))}
                </ul>
              </div>
            )}
            {/* Issues */}
            {result.caption_quality?.issues?.length > 0 && (
              <div className="card">
                <div className="card-title">❌ Issues Found</div>
                <ul className="suggestions">
                  {result.caption_quality.issues.map((issue, i) => (
                    <li key={i} style={{ borderLeft: '3px solid #ff6b6b' }}>{issue}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Row 3: Hashtag Analysis */}
          {result.hashtag_analysis && (
            <div className="card">
              <div className="card-title">
                #️⃣ Hashtag Relevance —{' '}
                <span style={{ color: '#fcb045' }}>
                  {result.hashtag_analysis.relevance_score}% relevant
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 12 }}>
                <div>
                  <div style={{ color: '#6bcb77', fontSize: '0.8rem', marginBottom: 8, fontWeight: 600 }}>
                    ✅ Relevant ({result.hashtag_analysis.relevant?.length})
                  </div>
                  {result.hashtag_analysis.relevant?.length > 0
                    ? result.hashtag_analysis.relevant.map((h, i) => (
                        <div key={i} style={{
                          background: '#0d1f0d',
                          border: '1px solid #1a3a1a',
                          borderRadius: 6,
                          padding: '4px 10px',
                          fontSize: '0.82rem',
                          color: '#6bcb77',
                          marginBottom: 6
                        }}>{h}</div>
                      ))
                    : <div style={{ color: '#444', fontSize: '0.82rem' }}>None detected</div>
                  }
                </div>
                <div>
                  <div style={{ color: '#ff6b6b', fontSize: '0.8rem', marginBottom: 8, fontWeight: 600 }}>
                    ❌ Not Relevant ({result.hashtag_analysis.irrelevant?.length})
                  </div>
                  {result.hashtag_analysis.irrelevant?.length > 0
                    ? result.hashtag_analysis.irrelevant.map((h, i) => (
                        <div key={i} style={{
                          background: '#1f0d0d',
                          border: '1px solid #3a1a1a',
                          borderRadius: 6,
                          padding: '4px 10px',
                          fontSize: '0.82rem',
                          color: '#ff6b6b',
                          marginBottom: 6
                        }}>{h}</div>
                      ))
                    : <div style={{ color: '#444', fontSize: '0.82rem' }}>All relevant!</div>
                  }
                </div>
                <div>
                  <div style={{ color: '#4d96ff', fontSize: '0.8rem', marginBottom: 8, fontWeight: 600 }}>
                    💡 Suggested for {category}
                  </div>
                  {result.hashtag_analysis.suggested?.map((h, i) => (
                    <div key={i} style={{
                      background: '#0d0d1f',
                      border: '1px solid #1a1a3a',
                      borderRadius: 6,
                      padding: '4px 10px',
                      fontSize: '0.82rem',
                      color: '#4d96ff',
                      marginBottom: 6,
                      cursor: 'pointer'
                    }}>{h}</div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Row 4: Improvement Suggestions */}
          {result.caption_quality?.suggestions?.length > 0 && (
            <div className="card">
              <div className="card-title">💡 How to Improve This Caption</div>
              <ul className="suggestions">
                {result.caption_quality.suggestions.map((s, i) => (
                  <li key={i} style={{ borderLeft: '3px solid #833ab4' }}>{s}</li>
                ))}
              </ul>
            </div>
          )}

        </div>
      )}
    </div>
  );
}