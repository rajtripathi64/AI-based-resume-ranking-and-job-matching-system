import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, FileText, UploadCloud } from 'lucide-react';
import FormMessage from '../components/FormMessage.jsx';
import { getMyResumes, uploadResume } from '../services/api.js';
import { getSavedToken, getSavedUser } from '../services/session.js';

function ResumeUploadPage() {
  const navigate = useNavigate();
  const user = getSavedUser();
  const token = getSavedToken();
  const [file, setFile] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadResumes() {
      if (!token) return;
      try {
        const data = await getMyResumes(token);
        setResumes(data);
      } catch {
        setMessage('Login as a candidate to view uploaded resumes.');
        setMessageType('error');
      }
    }
    loadResumes();
  }, [token]);

  async function handleSubmit(event) {
    event.preventDefault();
    if (!token) {
      navigate('/login');
      return;
    }
    if (!file) {
      setMessage('Please select a PDF, DOCX, or TXT resume.');
      setMessageType('error');
      return;
    }

    setLoading(true);
    setMessage('');
    try {
      const uploaded = await uploadResume(file, token);
      setResumes([uploaded, ...resumes]);
      setFile(null);
      event.target.reset();
      setMessage('Resume uploaded and parsed successfully.');
      setMessageType('success');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Resume upload failed.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="upload-page">
      <section className="upload-header">
        <div>
          <Link className="back-link" to={`/dashboard/${user?.role || 'candidate'}`}><ArrowLeft size={18} /> Dashboard</Link>
          <p className="dashboard-badge">Candidate Resume</p>
          <h1>Upload and parse resume</h1>
          <p>Upload a PDF, DOCX, or TXT file. The backend extracts text and stores it in SQL Server.</p>
        </div>
      </section>

      <section className="upload-grid">
        <article className="panel upload-panel">
          <div className="panel-heading">
            <div className="metric-icon"><UploadCloud size={20} /></div>
            <div>
              <h2>Resume file</h2>
              <p>Choose a readable resume document for parsing.</p>
            </div>
          </div>
          <form className="upload-form" onSubmit={handleSubmit}>
            <label className="file-drop-zone">
              <UploadCloud size={28} />
              <span>{file ? file.name : 'Select PDF, DOCX, or TXT resume'}</span>
              <input type="file" accept=".pdf,.docx,.txt" onChange={(event) => setFile(event.target.files?.[0] || null)} />
            </label>
            <FormMessage type={messageType}>{message}</FormMessage>
            <button className="primary-action" type="submit" disabled={loading}>
              <UploadCloud size={18} /> {loading ? 'Uploading...' : 'Upload resume'}
            </button>
          </form>
        </article>

        <article className="panel parsed-panel">
          <div className="panel-heading">
            <div className="metric-icon"><FileText size={20} /></div>
            <div>
              <h2>Parsed resumes</h2>
              <p>Recently uploaded resumes from your candidate account.</p>
            </div>
          </div>
          <div className="resume-list">
            {resumes.length === 0 && <p className="empty-state">No resumes uploaded yet.</p>}
            {resumes.map((resume) => (
              <article className="resume-item" key={resume.id}>
                <strong>{resume.file_name}</strong>
                <span>{resume.extracted_skills || 'No matching skill keywords found yet'}</span>
                <p>{resume.parsed_text_preview || 'No preview available.'}</p>
              </article>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}

export default ResumeUploadPage;
