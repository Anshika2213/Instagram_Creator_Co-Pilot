import React, { useState } from 'react';
import axios from 'axios';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
  ResponsiveContainer, RadarChart, Radar,
  PolarGrid, PolarAngleAxis
} from 'recharts';

const CATEGORIES = ['Beauty','Comedy','Fashion','Fitness','Food','Lifestyle','Music','Photography','Technology','Travel'];
const DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
const CONTENT_TYPES = ['image','reel','carousel'];

const GRADE_COLORS = { A: '#6bcb77', B: '#fcb045', C: '#4d96ff', D: '#ff9f43', F: '#ff6b6b' };
const SENTIMENT_COLORS = { Positive: '#6bcb77', Neutral: '#4d96ff', Negative: '#ff6b6b' };

export default function PrePostPredictor() {
  const [form, setForm] = useState({
    follower_count: 8000,
    content_type: 'reel',
    category: 'Fitness',
    post_hour: 19,
    day_of_week: 'Saturday',
    has_media: 1,
    is_verified: 0
  });

  const [caption, setCaption] = useState('');
  const [hashtagsText, setHashtagsText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handle = (e) => {
    const { name, value, type } = e.target;
    setForm(f => ({ ...f, [name]: type === 'number' ? Number(value) : value }));
  };

  const predict = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await axios.post('http://localhost:5000/predict-prepost', {
        ...form, caption, hashtags_text: hashtagsText
      });
      setResult(res.data);
    } catch (err) {
      setError('Could not connect to backend. Make sure Flask is running on port 5000.');
    }
    setLoading(false);
  };

  const buildScoreData = (quality) => {
    if (!quality) return [];
    return [
      { name: 'Length', value: quality.word_count >= 15 ? 2 : quality.word_count >= 8 ? 1 : 0, max: 2 },
      { name: 'Emojis', value: quality.emoji_count >= 1 ? 1 : 0, max: 1 },
      { name: 'Question', value: quality.has_question ? 2 : 0, max: 2 },
      { name: 'CTA', value: quality.has_cta ? 2 : 0, max: 2 },
      { name: 'Structure', value: 1, max: 1 },
      { name: 'Hashtags', value: quality.hashtag_count > 0 ? 1 : 0, max: 1 },
      { name: 'Original', value: 1, max: 1 },
    ];
  };

  const buildRadarData = (quality) => {
    if (!quality) return [];
    return [
      { metric: 'Length', value: quality.word_count >= 15 ? 100 : (quality.word_count / 15) * 100 },
      { metric: 'Emojis', value: quality.emoji_count >= 2 ? 100 : quality.emoji_count * 50 },
      { metric: 'Question', value: quality.has_question ? 100 : 0 },
      { metric: 'CTA', value: quality.has_cta ? 100 : 0 },
      { metric: 'Hashtags', value: Math.min(quality.hashtag_count * 10, 100) },
    ];
  };

  return (
    <div className="page-layout-single">
      {/* ── TOP: Input Form ── */}
      <div className="top-panel">
        <div className="desc-box">
          <strong>Model A — Pre-Post Predictor</strong><br />
          Write your caption and hashtags. NLP auto-extracts sentiment,
          length, and hashtag count — then predicts expected engagement
          and analyzes your caption quality before you post.
        </div>

        {/* Caption */}
        <div className="card">
          <div className="card-title">✍️ Caption & Hashtags</div>
          <div className="form-group full" style={{ marginBottom: 14 }}>
            <label>Your Caption</label>
            <textarea
              value={caption}
              onChange={e => setCaption(e.target.value)}
              placeholder="Write your Instagram caption here... NLP will auto-detect sentiment, length, and quality."
              rows={5}
            />
            <div style={{ color: '#333', fontSize: '0.73rem', marginTop: 4 }}>
              {caption.split(/\s+/).filter(w => w).length} words · {caption.length} chars
              {caption && (
                <span style={{ color: '#833ab4', marginLeft: 8 }}>
                  ✓ NLP auto-extracts sentiment + quality score
                </span>
              )}
            </div>
          </div>
          <div className="form-group full">
            <label>Hashtags (space or comma separated)</label>
            <input
              type="text"
              value={hashtagsText}
              onChange={e => setHashtagsText(e.target.value)}
              placeholder="#fitness #workout #gym #health"
            />
            <div style={{ color: '#333', fontSize: '0.73rem', marginTop: 4 }}>
              {hashtagsText.split(/[\s,]+/).filter(h => h.trim()).length} hashtags detected
              {hashtagsText && (
                <span style={{ color: '#833ab4', marginLeft: 8 }}>
                  ✓ NLP checks relevance for {form.category}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Post Details */}
        <div className="card">
          <div className="card-title">📋 Post Details</div>
          <div className="form-grid">
            <div className="form-group">
              <label>Follower Count</label>
              <input type="number" name="follower_count" value={form.follower_count} onChange={handle} />
            </div>
            <div className="form-group">
              <label>Content Category</label>
              <select name="category" value={form.category} onChange={handle}>
                {CATEGORIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Content Type</label>
              <select name="content_type" value={form.content_type} onChange={handle}>
                {CONTENT_TYPES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Post Hour (0-23)</label>
              <input type="number" name="post_hour" value={form.post_hour} onChange={handle} min={0} max={23} />
            </div>
            <div className="form-group">
              <label>Day of Week</label>
              <select name="day_of_week" value={form.day_of_week} onChange={handle}>
                {DAYS.map(d => <option key={d}>{d}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Has Media?</label>
              <select name="has_media" value={form.has_media} onChange={handle}>
                <option value={1}>Yes</option>
                <option value={0}>No</option>
              </select>
            </div>
            <div className="form-group">
              <label>Verified Account?</label>
              <select name="is_verified" value={form.is_verified} onChange={handle}>
                <option value={0}>No</option>
                <option value={1}>Yes</option>
              </select>
            </div>
          </div>
          <button className="btn" onClick={predict} disabled={loading}>
            {loading ? '⏳ Running NLP + Prediction...' : '🔮 Predict Engagement'}
          </button>
        </div>

        {error && <div className="error-box">⚠️ {error}</div>}
      </div>

      {/* ── BOTTOM: Results Panel ── */}
      {loading && (
        <div className="bottom-loading">
          <div className="empty-icon">🧠</div>
          <p>Running DistilBERT + spaCy + XGBoost<span className="loading-dots" /></p>
        </div>
      )}

      {result && (
        <div className="bottom-panel">
            {/* ── 1. NLP Auto-Extracted + Prediction — full width ── */}
            <div style={{ gridColumn: '1 / -1' }}><div className="result-header-card">
              <div style={{ color: '#555', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
                🤖 NLP Auto-Extracted Features
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10, marginBottom: 16 }}>
                <div className="metric-card">
                  <div className="metric-value" style={{
                    color: SENTIMENT_COLORS[result.auto_extracted?.sentiment] || '#fff',
                    fontSize: '0.95rem'
                  }}>
                    {result.auto_extracted?.sentiment}
                  </div>
                  <div className="metric-label">Sentiment · DistilBERT</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{result.auto_extracted?.caption_length}</div>
                  <div className="metric-label">Words</div>
                </div>
                <div className="metric-card">
                  <div className="metric-value">{result.auto_extracted?.hashtags_count}</div>
                  <div className="metric-label">Hashtags</div>
                </div>
              </div>

              {/* Predicted Engagement */}
              <div style={{ paddingTop: 16, borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                  <div>
                    <div style={{ color: '#555', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>
                      Predicted Engagement Rate
                    </div>
                    <div style={{ fontSize: '2.6rem', fontWeight: 900, color: '#fcb045' }}>
                      {result.predicted_engagement_display}
                    </div>
                  </div>
                  <div style={{
                    padding: '6px 18px', borderRadius: 20,
                    background: '#833ab4', color: '#fff',
                    fontWeight: 800, fontSize: '0.82rem'
                  }}>
                    {result.interpretation}
                  </div>
                </div>
                <div style={{ color: '#333', fontSize: '0.73rem', marginTop: 6 }}>
                  {result.disclaimer}
                </div>
              </div>
            </div></div>

            {/* ── 2. Caption Quality Score + Bar Chart ── */}
            {result.caption_quality && (
              <div className="result-card">
                <div className="chart-title">
                  📝 Caption Quality —{' '}
                  <span style={{ color: GRADE_COLORS[result.caption_quality.grade] }}>
                    {result.caption_quality.score}/{result.caption_quality.max_score} · Grade {result.caption_quality.grade}
                  </span>
                </div>

                {/* Stats row */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 8, marginBottom: 14 }}>
                  <div className="metric-card">
                    <div className="metric-value">{result.caption_quality.word_count}</div>
                    <div className="metric-label">Words</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value">{result.caption_quality.emoji_count}</div>
                    <div className="metric-label">Emojis</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value" style={{ color: result.caption_quality.has_question ? '#6bcb77' : '#ff6b6b' }}>
                      {result.caption_quality.has_question ? '✓' : '✗'}
                    </div>
                    <div className="metric-label">Question</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value" style={{ color: result.caption_quality.has_cta ? '#6bcb77' : '#ff6b6b' }}>
                      {result.caption_quality.has_cta ? '✓' : '✗'}
                    </div>
                    <div className="metric-label">CTA</div>
                  </div>
                </div>

                {/* Bar chart */}
                <ResponsiveContainer width="100%" height={140}>
                  <BarChart data={buildScoreData(result.caption_quality)} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                    <XAxis dataKey="name" tick={{ fill: '#555', fontSize: 10 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fill: '#444', fontSize: 10 }} axisLine={false} tickLine={false} domain={[0, 2]} />
                    <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: '0.8rem' }} />
                    <Bar dataKey="value" radius={[4,4,0,0]}>
                      {buildScoreData(result.caption_quality).map((entry, i) => (
                        <Cell key={i} fill={entry.value === entry.max ? '#6bcb77' : entry.value > 0 ? '#fcb045' : '#ff6b6b'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* ── 3. Caption Quality Radar ── */}
            {result.caption_quality && (
              <div className="result-card">
                <div className="chart-title">🕸️ Caption Quality Radar</div>
                <ResponsiveContainer width="100%" height={200}>
                  <RadarChart data={buildRadarData(result.caption_quality)}>
                    <PolarGrid stroke="#1e1e1e" />
                    <PolarAngleAxis dataKey="metric" tick={{ fill: '#555', fontSize: 10 }} />
                    <Radar
                      dataKey="value"
                      stroke="#fd1d1d"
                      fill="#fd1d1d"
                      fillOpacity={0.2}
                      strokeWidth={2}
                    />
                    <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8, fontSize: '0.8rem' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* ── 4. Hashtag Relevance ── */}
            {result.hashtag_analysis && (result.hashtag_analysis.relevant?.length + result.hashtag_analysis.irrelevant?.length) > 0 && (
              <div className="result-card">
                <div className="chart-title">
                  #️⃣ Hashtag Relevance — {result.hashtag_analysis.relevance_score}% relevant to {form.category}
                </div>
                <div style={{ marginBottom: 10 }}>
                  <div style={{ color: '#555', fontSize: '0.72rem', marginBottom: 6 }}>Your hashtags:</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                    {result.hashtag_analysis.relevant?.map((h, i) => (
                      <span key={i} className="tag-pill tag-relevant">{h}</span>
                    ))}
                    {result.hashtag_analysis.irrelevant?.map((h, i) => (
                      <span key={i} className="tag-pill tag-irrelevant">{h}</span>
                    ))}
                  </div>
                </div>
                {result.hashtag_analysis.suggested?.length > 0 && (
                  <div>
                    <div style={{ color: '#555', fontSize: '0.72rem', marginBottom: 6 }}>💡 Suggested for {form.category}:</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap' }}>
                      {result.hashtag_analysis.suggested.map((h, i) => (
                        <span key={i} className="tag-pill tag-suggested">{h}</span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ── 5. Caption Issues ── */}
            {result.caption_quality?.issues?.length > 0 && (
              <div className="result-card">
                <div className="chart-title">❌ Caption Issues</div>
                <ul className="suggestions">
                  {result.caption_quality.issues.map((issue, i) => (
                    <li key={i} style={{ borderLeft: '3px solid #ff6b6b' }}>{issue}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* ── 6. All Recommendations ── */}
            <div className="result-card">
              <div className="chart-title">💡 All Recommendations</div>
              <ul className="suggestions">
                {/* Caption improvement suggestions */}
                {result.caption_quality?.suggestions?.map((s, i) => (
                  <li key={`cap-${i}`} style={{ borderLeft: '3px solid #fd1d1d' }}>{s}</li>
                ))}
                {/* Data-driven posting suggestions */}
                {result.suggestions?.map((s, i) => (
                  <li key={`post-${i}`} style={{ borderLeft: '3px solid #833ab4' }}>{s}</li>
                ))}
              </ul>
            </div>
        </div>
      )}
    </div>
  );
}