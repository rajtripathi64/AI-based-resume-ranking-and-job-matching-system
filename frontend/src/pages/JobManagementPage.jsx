import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, BriefcaseBusiness, ClipboardList, PlusCircle, Trash2 } from 'lucide-react';
import FormMessage from '../components/FormMessage.jsx';
import { createJob, deleteJob, getMyJobs } from '../services/api.js';
import { getSavedToken, getSavedUser } from '../services/session.js';

const initialForm = {
  title: '',
  location: '',
  min_experience: '0',
  status: 'open',
  description: '',
};

function JobManagementPage() {
  const navigate = useNavigate();
  const user = getSavedUser();
  const token = getSavedToken();
  const [form, setForm] = useState(initialForm);
  const [jobs, setJobs] = useState([]);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadJobs() {
      if (!token) return;
      try {
        const data = await getMyJobs(token);
        setJobs(data);
      } catch {
        setMessage('Login as a company user to manage jobs.');
        setMessageType('error');
      }
    }
    loadJobs();
  }, [token]);

  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!token) {
      navigate('/login');
      return;
    }

    setLoading(true);
    setMessage('');
    try {
      const created = await createJob({
        ...form,
        min_experience: Number(form.min_experience || 0),
      }, token);
      setJobs([created, ...jobs]);
      setForm(initialForm);
      setMessage('Job description created and skills extracted successfully.');
      setMessageType('success');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Job creation failed.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(jobId) {
    if (!token) return;
    try {
      await deleteJob(jobId, token);
      setJobs(jobs.filter((job) => job.id !== jobId));
      setMessage('Job deleted successfully.');
      setMessageType('success');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Could not delete job.');
      setMessageType('error');
    }
  }

  return (
    <main className="jobs-page">
      <section className="upload-header">
        <div>
          <Link className="back-link" to={`/dashboard/${user?.role || 'company'}`}><ArrowLeft size={18} /> Dashboard</Link>
          <p className="dashboard-badge">Company Jobs</p>
          <h1>Create job descriptions</h1>
          <p>Add job requirements so the matching phase can rank candidates against clear role data.</p>
        </div>
      </section>

      <section className="jobs-grid">
        <article className="panel job-form-panel">
          <div className="panel-heading">
            <div className="metric-icon"><PlusCircle size={20} /></div>
            <div>
              <h2>New job</h2>
              <p>Write a clear description with skills, tools, and experience needs.</p>
            </div>
          </div>
          <form className="job-form" onSubmit={handleSubmit}>
            <label>
              Job title
              <input name="title" value={form.title} onChange={updateField} placeholder="Machine Learning Engineer" required />
            </label>
            <div className="form-row">
              <label>
                Location
                <input name="location" value={form.location} onChange={updateField} placeholder="Noida / Remote" />
              </label>
              <label>
                Min experience
                <input name="min_experience" type="number" min="0" step="0.5" value={form.min_experience} onChange={updateField} />
              </label>
            </div>
            <label>
              Status
              <select name="status" value={form.status} onChange={updateField}>
                <option value="open">Open</option>
                <option value="closed">Closed</option>
              </select>
            </label>
            <label>
              Job description
              <textarea name="description" value={form.description} onChange={updateField} placeholder="Mention skills like Python, SQL Server, React, NLP, BERT, XGBoost..." required />
            </label>
            <FormMessage type={messageType}>{message}</FormMessage>
            <button className="primary-action" type="submit" disabled={loading}>
              <BriefcaseBusiness size={18} /> {loading ? 'Saving...' : 'Create job'}
            </button>
          </form>
        </article>

        <article className="panel jobs-list-panel">
          <div className="panel-heading">
            <div className="metric-icon"><ClipboardList size={20} /></div>
            <div>
              <h2>Company jobs</h2>
              <p>Saved jobs with extracted skill keywords.</p>
            </div>
          </div>
          <div className="job-list">
            {jobs.length === 0 && <p className="empty-state">No jobs created yet.</p>}
            {jobs.map((job) => (
              <article className="job-item" key={job.id}>
                <div className="job-item-header">
                  <div>
                    <strong>{job.title}</strong>
                    <span>{job.location || 'Location not specified'} | {job.min_experience} years | {job.status}</span>
                  </div>
                  <button className="icon-danger-button" type="button" onClick={() => handleDelete(job.id)} aria-label="Delete job">
                    <Trash2 size={18} />
                  </button>
                </div>
                <p>{job.description}</p>
                <small>{job.required_skills || 'No matching skill keywords found yet'}</small>
              </article>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}

export default JobManagementPage;
