import React, { useState } from 'react';
import axios from 'axios';
import {
  RadialBarChart, RadialBar, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
  RadarChart, Radar, PolarGrid, PolarAngleAxis,
  PieChart, Pie, Legend
} from 'recharts';

const CATEGORIES = ['Beauty','Comedy','Fashion','Fitness','Food','Lifestyle','Music','Photography','Technology','Travel'];
const DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'];
const MEDIA_TYPES = ['image','reel','carousel'];
const TRAFFIC_SOURCES = ['Explore','External','Hashtags','Home Feed','Profile','Reels Feed'];
const ACCOUNT_TYPES = ['creator','brand'];

const PERF_COLORS = {
  'Top Performer': '#fcb045',
  'Above Average': '#6bcb77',
  'Average': '#4d96ff',
  'Below Average': '#ff6b6b'
};

const LABEL_MAP = {
  'viral': 'Top Performer',
  'high': 'Above Average',
  'medium': 'Average',
  'low': 'Below Average'
};

const METRIC_COLORS = ['#833ab4','#fd1d1d','#fcb045','#6bcb77','#4d96ff','#ff6b6b'];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{
        background: '#1a1a1a', border: '1px solid #333',
        borderRadius: 8, padding: '10px 14px', fontSize: '0.82rem'
      }}>
        <div style={{ color: '#888', marginBottom: 4 }}>{label}</div>
        {payload.map((p, i) => (
          <div key={i} style={{ color: p.color || '#fff' }}>
            {p.name}: <strong>{typeof p.value === 'number' ? p.value.toFixed(4) : p.value}</strong>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function PerformanceAnalyzer() {
  const [form, setForm] = useState({
    likes: 180, comments: 6, shares: 8, saves: 12,
    reach: 3200, impressions: 4500, follower_count: 8000,
    hashtags_count: 5, post_hour: 14, caption_length: 100,
    media_type: 'image', content_category: 'Fitness',
    traffic_source: 'Home Feed', has_call_to_action: 0,
    day_of_week: 'Monday', account_type: 'creator'
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // made a change here (28.06.2026)

  const handle = (e) => {
  const { name, value } = e.target;

  setForm(f => ({
    ...f,
    [name]: value
    }));
  };

  const analyze = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await axios.post('http://localhost:5000/predict-performance', form);
      setResult(res.data);
    } catch (err) {
      setError('Could not connect to backend. Make sure Flask is running on port 5000.');
    }
    setLoading(false);
  };

  // Chart data builders
  const buildRadarData = (metrics) => {
    if (!metrics) return [];
    return [
      { metric: 'Save Ratio', value: Math.min(metrics.save_ratio * 1000, 100) },
      { metric: 'Share Ratio', value: Math.min(metrics.share_ratio * 1000, 100) },
      { metric: 'Like Ratio', value: Math.min(metrics.like_ratio * 100, 100) },
      { metric: 'Comment Ratio', value: Math.min(metrics.comment_ratio * 1000, 100) },
      { metric: 'CTR', value: Math.min(metrics.ctr * 100, 100) },
      { metric: 'Eng. Rate', value: Math.min(metrics.engagement_rate * 10, 100) },
    ];
  };

  const buildProbData = (probs) => {
    if (!probs) return [];
    return Object.entries(probs).map(([label, value]) => {
      const displayName = LABEL_MAP[label] || label;
      return { name: displayName, value, fill: PERF_COLORS[displayName] || '#555' };
    });
  };

  const buildMetricsBar = (metrics) => {
    if (!metrics) return [];
    return [
      { name: 'Save Ratio', value: parseFloat((metrics.save_ratio * 1000).toFixed(2)) },
      { name: 'Share Ratio', value: parseFloat((metrics.share_ratio * 1000).toFixed(2)) },
      { name: 'Like Ratio', value: parseFloat((metrics.like_ratio * 100).toFixed(2)) },
      { name: 'CTR', value: parseFloat((metrics.ctr * 100).toFixed(2)) },
    ];
  };

  const perfClass = result ? {
    'Top Performer': 'perf-top',
    'Above Average': 'perf-above',
    'Average': 'perf-average',
    'Below Average': 'perf-below'
  }[LABEL_MAP[result.performance_category] || result.performance_category] || 'perf-average' : '';

  return (
    <div className="page-layout-single">
      {/* ── TOP: Input Form ── */}
      <div className="top-panel">
        <div className="desc-box">
          <strong>Model B — Post-Performance Analyzer</strong><br />
          Enter your post's engagement data after it's been live. The model classifies
          performance and shows charts explaining exactly why it's performing the way it is.
        </div>

        <div className="card">
          <div className="card-title">📈 Engagement Numbers</div>
          <div className="form-grid">
            {['likes','comments','shares','saves','reach','impressions'].map(field => (
              <div className="form-group" key={field}>
                <label>{field.charAt(0).toUpperCase() + field.slice(1)}</label>
                <input type="number" name={field} value={form[field]} onChange={handle} />
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-title">📋 Post Details</div>
          <div className="form-grid">
            <div className="form-group">
              <label>Follower Count</label>
              <input type="number" name="follower_count" value={form.follower_count} onChange={handle} />
            </div>
            <div className="form-group">
              <label>Content Category</label>
              <select name="content_category" value={form.content_category} onChange={handle}>
                {CATEGORIES.map(c => <option key={c}>{c}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Media Type</label>
              <select name="media_type" value={form.media_type} onChange={handle}>
                {MEDIA_TYPES.map(m => <option key={m}>{m}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Traffic Source</label>
              <select name="traffic_source" value={form.traffic_source} onChange={handle}>
                {TRAFFIC_SOURCES.map(t => <option key={t}>{t}</option>)}
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
              <label>Caption Length</label>
              <input type="number" name="caption_length" value={form.caption_length} onChange={handle} />
            </div>
            <div className="form-group">
              <label>Hashtag Count</label>
              <input type="number" name="hashtags_count" value={form.hashtags_count} onChange={handle} />
            </div>
            <div className="form-group">
              <label>Has Call to Action?</label>
              <select name="has_call_to_action" value={form.has_call_to_action} onChange={handle}>
                <option value={1}>Yes</option>
                <option value={0}>No</option>
              </select>
            </div>
            <div className="form-group">
              <label>Account Type</label>
              <select name="account_type" value={form.account_type} onChange={handle}>
                {ACCOUNT_TYPES.map(a => <option key={a}>{a}</option>)}
              </select>
            </div>
          </div>
          <button className="btn" onClick={analyze} disabled={loading}>
            {loading ? '⏳ Analyzing...' : '📊 Analyze Performance'}
          </button>
        </div>

        {error && <div className="error-box">⚠️ {error}</div>}
      </div>

      {/* ── BOTTOM: Results Panel ── */}
      {loading && (
        <div className="bottom-loading">
          <div className="empty-icon">⚙️</div>
          <p>Running XGBoost model<span className="loading-dots" /></p>
        </div>
      )}

      {result && (
        <div className="bottom-panel">
          {/* Performance Header — full width */}
          <div style={{ gridColumn: '1 / -1' }}><div className="result-header-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <div style={{ color: '#555', fontSize: '0.72rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>
                    Performance Classification
                  </div>
                  <div style={{
                    fontSize: '2.2rem', fontWeight: 900,
                    color: PERF_COLORS[LABEL_MAP[result.performance_category]] || '#fff',
                    marginBottom: 8
                  }}>
                    {LABEL_MAP[result.performance_category] || result.performance_category}
                  </div>
                  <span className={`perf-badge ${perfClass}`}>
                    {result.confidence} confidence
                  </span>
                </div>
                {/* <div style={{ textAlign: 'right' }}>
                  <div style={{ color: '#555', fontSize: '0.72rem', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Engagement Rate
                  </div>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: '#fcb045' }}>
                    {result.key_metrics?.engagement_rate}%
                  </div>
                </div> */}
              </div>
            </div></div>

            {/* Probability Breakdown — Pie Chart */}
            <div className="result-card">
              <div className="chart-title">📊 Performance Probability Breakdown</div>
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={buildProbData(result.probability_breakdown)}
                    cx="50%" cy="50%"
                    innerRadius={50} outerRadius={80}
                    paddingAngle={3}
                    dataKey="value"
                    fill="none"
                  >
                    {buildProbData(result.probability_breakdown).map((entry, i) => (
                      <Cell key={i} fill={PERF_COLORS[entry.name] || '#555'} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip formatter={(val) => `${val}%`} contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8 }} />
                  <Legend
                    formatter={(value) => <span style={{ color: '#888', fontSize: '0.78rem' }}>{value}</span>}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Engagement Metrics — Bar Chart */}
            <div className="result-card">
              <div className="chart-title">📈 Engagement Signal Strengths (scaled)</div>
              <ResponsiveContainer width="100%" height={180}>
                <BarChart data={buildMetricsBar(result.key_metrics)} margin={{ top: 0, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="name" tick={{ fill: '#555', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fill: '#444', fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="value" radius={[4,4,0,0]}>
                    {buildMetricsBar(result.key_metrics).map((_, i) => (
                      <Cell key={i} fill={METRIC_COLORS[i % METRIC_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Radar Chart */}
            <div className="result-card">
              <div className="chart-title">🕸️ Engagement Profile Radar</div>
              <ResponsiveContainer width="100%" height={220}>
                <RadarChart data={buildRadarData(result.key_metrics)}>
                  <PolarGrid stroke="#1e1e1e" />
                  <PolarAngleAxis dataKey="metric" tick={{ fill: '#555', fontSize: 10 }} />
                  <Radar
                    name="Your Post"
                    dataKey="value"
                    stroke="#833ab4"
                    fill="#833ab4"
                    fillOpacity={0.25}
                    strokeWidth={2}
                  />
                  <Tooltip contentStyle={{ background: '#1a1a1a', border: '1px solid #333', borderRadius: 8 }} />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            {/* Raw Metrics Grid */}
            <div className="result-card">
              <div className="chart-title">🔢 Raw Metric Values</div>
              <div className="metrics-grid">
                {Object.entries(result.key_metrics || {}).map(([key, val]) => (
                  <div className="metric-card" key={key}>
                    <div className="metric-value">{val}</div>
                    <div className="metric-label">{key.replace(/_/g, ' ')}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Warnings */}
            {result.warnings?.length > 0 && (
              <div className="result-card">
                <div className="chart-title">⚠️ Issues Detected</div>
                <ul className="suggestions">
                  {result.warnings.map((w, i) => (
                    <li key={i} style={{ borderLeft: '3px solid #ff6b6b' }}>{w}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Suggestions */}
            {result.suggestions?.length > 0 && (
              <div className="result-card">
                <div className="chart-title">💡 Recommendations</div>
                <ul className="suggestions">
                  {result.suggestions.map((s, i) => (
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