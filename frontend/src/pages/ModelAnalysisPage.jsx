import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, BarChart3, BrainCircuit, Database, Play, ShieldCheck, Trophy } from 'lucide-react';
import FormMessage from '../components/FormMessage.jsx';
import { getModelComparison, getModelRuns, trainModels } from '../services/api.js';
import { getSavedToken, getSavedUser } from '../services/session.js';

function metricValue(value) {
  if (value === null || value === undefined || value === '') return '0.00';
  return Number(value).toFixed(2);
}

function ModelAnalysisPage() {
  const navigate = useNavigate();
  const token = getSavedToken();
  const user = getSavedUser();
  const [maxSamples, setMaxSamples] = useState(2385);
  const [threshold, setThreshold] = useState(75);
  const [comparison, setComparison] = useState([]);
  const [runs, setRuns] = useState([]);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [isLoading, setIsLoading] = useState(false);

  const bestModel = useMemo(() => comparison[0], [comparison]);

  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    async function loadResults() {
      try {
        const [comparisonData, runData] = await Promise.all([
          getModelComparison(token),
          getModelRuns(token),
        ]);
        setComparison(comparisonData);
        setRuns(runData.slice(0, 8));
      } catch (error) {
        setMessage({
          type: 'error',
          text: error.response?.status === 403
            ? 'Only admin users can open model training analysis.'
            : 'Unable to load model results yet. Train once to create comparison data.',
        });
      }
    }
    loadResults();
  }, [navigate, token]);

  async function handleTrain(event) {
    event.preventDefault();
    setIsLoading(true);
    setMessage({ type: '', text: '' });
    try {
      const result = await trainModels({ maxSamples, threshold }, token);
      const freshRuns = await getModelRuns(token);
      setComparison(result.results);
      setRuns(freshRuns.slice(0, 8));
      setMessage({
        type: 'success',
        text: `Training completed on ${result.dataset_name} with ${result.max_samples} samples.`,
      });
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Training failed. Check backend terminal for details.',
      });
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="ml-page">
      <header className="upload-header ml-header">
        <Link className="back-link" to={`/dashboard/${user?.role || 'admin'}`}><ArrowLeft size={18} /> Back to dashboard</Link>
        <p className="dashboard-badge">Phase 9 Model Training</p>
        <h1>Comparative model analysis</h1>
        <p>Train multiple ML models on the Hugging Face resume-job fit dataset and compare which method gives the best screening performance.</p>
      </header>

      <section className="ml-hero-grid">
        <article className="panel ml-train-panel">
          <div className="panel-heading">
            <div className="metric-icon"><BrainCircuit size={20} /></div>
            <div>
              <h2>Train models</h2>
              <p>Uses Logistic Regression, SVM, KNN, Random Forest, and XGBoost.</p>
            </div>
          </div>
          <form className="ml-train-form" onSubmit={handleTrain}>
            <label>
              Dataset samples
              <input min="100" max="10000" step="1" type="number" value={maxSamples} onChange={(event) => setMaxSamples(Number(event.target.value))} />
            </label>
            <label>
              Match threshold (%)
              <input min="1" max="99" step="1" type="number" value={threshold} onChange={(event) => setThreshold(Number(event.target.value))} />
            </label>
            <button className="primary-action" type="submit" disabled={isLoading}>
              <Play size={18} /> {isLoading ? 'Training models...' : 'Start training'}
            </button>
            {message.text && <FormMessage type={message.type}>{message.text}</FormMessage>}
          </form>
        </article>

        <article className="panel ml-best-panel">
          <div className="panel-heading">
            <div className="metric-icon"><Trophy size={20} /></div>
            <div>
              <h2>Best model</h2>
              <p>Sorted by F1 score because ranking needs balance between precision and recall.</p>
            </div>
          </div>
          {bestModel ? (
            <div className="best-model-card">
              <strong>{bestModel.model_name}</strong>
              <span>{metricValue(bestModel.f1_score)}% F1 score</span>
              <small>{bestModel.dataset_name}</small>
            </div>
          ) : (
            <p className="empty-state">No completed model run yet.</p>
          )}
        </article>
      </section>

      <section className="panel ml-table-panel">
        <div className="panel-heading">
          <div className="metric-icon"><BarChart3 size={20} /></div>
          <div>
            <h2>Latest comparison</h2>
            <p>Higher precision means fewer weak candidates pass; higher recall means fewer good candidates are missed.</p>
          </div>
        </div>
        <div className="ml-table-wrap">
          <table className="ml-table">
            <thead>
              <tr>
                <th>Model</th>
                <th>Accuracy</th>
                <th>Precision</th>
                <th>Recall</th>
                <th>F1</th>
              </tr>
            </thead>
            <tbody>
              {comparison.map((run) => (
                <tr key={run.id}>
                  <td>{run.model_name}</td>
                  <td>{metricValue(run.accuracy)}%</td>
                  <td>{metricValue(run.precision_score)}%</td>
                  <td>{metricValue(run.recall_score)}%</td>
                  <td><strong>{metricValue(run.f1_score)}%</strong></td>
                </tr>
              ))}
              {!comparison.length && (
                <tr><td colSpan="5">Train models to create comparison rows.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="panel ml-history-panel">
        <div className="panel-heading">
          <div className="metric-icon"><Database size={20} /></div>
          <div>
            <h2>Saved training runs</h2>
            <p>Recent runs stored in SQL Server model_runs table.</p>
          </div>
        </div>
        <div className="run-list">
          {runs.map((run) => (
            <article className="run-item" key={run.id}>
              <ShieldCheck size={18} />
              <div>
                <strong>{run.model_name}</strong>
                <span>{metricValue(run.f1_score)}% F1 | {new Date(run.created_at).toLocaleString()}</span>
              </div>
            </article>
          ))}
          {!runs.length && <p className="empty-state">No saved runs found.</p>}
        </div>
      </section>
    </main>
  );
}

export default ModelAnalysisPage;
