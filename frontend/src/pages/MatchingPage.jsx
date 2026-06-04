import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, BarChart3, FileText, Sparkles, UploadCloud, Users } from 'lucide-react';
import FormMessage from '../components/FormMessage.jsx';
import { instantCandidateMatch, instantCompanyMatch } from '../services/api.js';
import { getSavedToken, getSavedUser } from '../services/session.js';

function SkillChips({ skills = [], emptyText = 'No matched skills found' }) {
  return (
    <div className="matched-skills-block">
      <small>Matched skills</small>
      <div className="matched-skill-chips">
        {skills.length > 0
          ? skills.slice(0, 14).map((skill) => <span key={skill}>{skill}</span>)
          : <span>{emptyText}</span>}
      </div>
    </div>
  );
}

function MatchingPage() {
  const user = getSavedUser();
  const token = getSavedToken();
  const role = user?.role || 'candidate';
  const [candidateResume, setCandidateResume] = useState(null);
  const [candidateJdFile, setCandidateJdFile] = useState(null);
  const [candidateJdText, setCandidateJdText] = useState('');
  const [companyJdFile, setCompanyJdFile] = useState(null);
  const [companyJdText, setCompanyJdText] = useState('');
  const [companyResumeFiles, setCompanyResumeFiles] = useState([]);
  const [candidateNames, setCandidateNames] = useState('');
  const [results, setResults] = useState([]);
  const [directMatch, setDirectMatch] = useState(null);
  const [method, setMethod] = useState('Hybrid AI ranking');
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('info');
  const [loading, setLoading] = useState(false);

  async function runCandidateInstantMatch(event) {
    event.preventDefault();
    if (!candidateResume || (!candidateJdText && !candidateJdFile)) {
      setMessage('Upload your resume and provide a job description.');
      setMessageType('error');
      return;
    }
    setLoading(true);
    try {
      const data = await instantCandidateMatch({ resumeFile: candidateResume, jdText: candidateJdText, jdFile: candidateJdFile }, token);
      setDirectMatch(data.match);
      setResults([]);
      setMethod(data.method);
      setMessage('Resume and JD matched successfully.');
      setMessageType('success');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Candidate matching failed.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  }

  async function runCompanyInstantMatch(event) {
    event.preventDefault();
    if (companyResumeFiles.length === 0 || (!companyJdText && !companyJdFile)) {
      setMessage('Upload a JD and at least one candidate resume.');
      setMessageType('error');
      return;
    }
    setLoading(true);
    try {
      const data = await instantCompanyMatch({ candidateNames, jdText: companyJdText, jdFile: companyJdFile, resumeFiles: companyResumeFiles }, token);
      setDirectMatch(null);
      setResults(data.results || []);
      setMethod(data.method);
      setMessage('Top candidates ranked successfully.');
      setMessageType('success');
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Company matching failed.');
      setMessageType('error');
    } finally {
      setLoading(false);
    }
  }

  const isRecruiter = role === 'company';

  return (
    <main className="matching-page">
      <section className="upload-header matching-hero">
        <Link className="back-link" to={`/dashboard/${role}`}><ArrowLeft size={18} /> Dashboard</Link>
        <p className="dashboard-badge">AI Matching</p>
        <h1>{isRecruiter ? 'Recruiter candidate ranking' : 'Candidate resume matching'}</h1>
        <p>{isRecruiter ? 'Upload one JD and multiple resumes to get a ranked shortlist.' : 'Upload your resume, add a JD, and view your match percentage with matched skills.'}</p>
      </section>

      {isRecruiter ? (
        <section className="matching-workspace single">
          <article className="panel matching-control-panel">
            <div className="panel-heading">
              <div className="metric-icon"><Users size={20} /></div>
              <div>
                <h2>Matching</h2>
                <p>{method}</p>
              </div>
            </div>
            <form className="matching-controls" onSubmit={runCompanyInstantMatch}>
              <label>
                Job description
                <textarea value={companyJdText} onChange={(event) => setCompanyJdText(event.target.value)} placeholder="Paste JD requirements here." />
              </label>
              <div className="matching-file-row">
                <label className="file-drop-zone compact">
                  <FileText size={22} />
                  <span>{companyJdFile ? companyJdFile.name : 'Optional JD file'}</span>
                  <input type="file" accept=".pdf,.docx,.txt" onChange={(event) => setCompanyJdFile(event.target.files?.[0] || null)} />
                </label>
                <label className="file-drop-zone compact">
                  <UploadCloud size={22} />
                  <span>{companyResumeFiles.length ? `${companyResumeFiles.length} resumes selected` : 'Candidate resumes'}</span>
                  <input type="file" accept=".pdf,.docx,.txt" multiple onChange={(event) => setCompanyResumeFiles(Array.from(event.target.files || []))} />
                </label>
              </div>
              <label>
                Candidate names
                <input value={candidateNames} onChange={(event) => setCandidateNames(event.target.value)} placeholder="Optional: Asha, Vikram, Rahul" />
              </label>
              <button className="primary-action" type="submit" disabled={loading}>
                <BarChart3 size={18} /> {loading ? 'Ranking...' : 'Rank candidates'}
              </button>
            </form>
            <FormMessage type={messageType}>{message}</FormMessage>
          </article>

          <article className="panel matching-results-panel">
            <div className="panel-heading">
              <div className="metric-icon"><FileText size={20} /></div>
              <div>
                <h2>Top candidates</h2>
                <p>Ranked by final hybrid score.</p>
              </div>
            </div>
            <div className="match-list">
              {results.length === 0 && <p className="empty-state">Run matching to see ranked candidates.</p>}
              {results.map((item, index) => (
                <article className="match-item" key={`${item.file_name}-${index}`}>
                  <div className="match-rank">#{index + 1}</div>
                  <div className="match-info">
                    <strong>{item.candidate_name}</strong>
                    <span>{item.file_name}</span>
                    {item.email && <span>{item.email}</span>}
                    <SkillChips skills={item.matched_skills || []} />
                  </div>
                  <div className="match-score">{item.final_score}%</div>
                </article>
              ))}
            </div>
          </article>
        </section>
      ) : (
        <section className="matching-workspace candidate-simple">
          <article className="panel matching-control-panel">
            <div className="panel-heading">
              <div className="metric-icon"><UploadCloud size={20} /></div>
              <div>
                <h2>Resume parser</h2>
                <p>Select the resume file that will be parsed for skills.</p>
              </div>
            </div>
            <label className="file-drop-zone compact parser-drop-zone">
              <UploadCloud size={24} />
              <span>{candidateResume ? candidateResume.name : 'Upload resume PDF, DOCX, or TXT'}</span>
              <input type="file" accept=".pdf,.docx,.txt" onChange={(event) => setCandidateResume(event.target.files?.[0] || null)} />
            </label>
          </article>

          <article className="panel matching-control-panel">
            <div className="panel-heading">
              <div className="metric-icon"><Sparkles size={20} /></div>
              <div>
                <h2>Matching</h2>
                <p>{method}</p>
              </div>
            </div>
            <form className="matching-controls" onSubmit={runCandidateInstantMatch}>
              <label>
                Job description
                <textarea value={candidateJdText} onChange={(event) => setCandidateJdText(event.target.value)} placeholder="Paste company JD here." />
              </label>
              <label className="file-drop-zone compact">
                <FileText size={22} />
                <span>{candidateJdFile ? candidateJdFile.name : 'Optional JD file'}</span>
                <input type="file" accept=".pdf,.docx,.txt" onChange={(event) => setCandidateJdFile(event.target.files?.[0] || null)} />
              </label>
              <button className="primary-action" type="submit" disabled={loading}>
                <BarChart3 size={18} /> {loading ? 'Matching...' : 'Check match'}
              </button>
            </form>
            <FormMessage type={messageType}>{message}</FormMessage>
          </article>

          <article className="panel matching-results-panel candidate-result-panel">
            <div className="panel-heading">
              <div className="metric-icon"><FileText size={20} /></div>
              <div>
                <h2>Result</h2>
                <p>Final score and matched skills.</p>
              </div>
            </div>
            {directMatch ? (
              <article className="match-item direct-match-card">
                <div className="match-rank"><Sparkles size={18} /></div>
                <div className="match-info">
                  <strong>{directMatch.file_name}</strong>
                  <span>Resume compared with provided JD</span>
                  <SkillChips skills={directMatch.matched_skills || []} />
                </div>
                <div className="match-score">{directMatch.final_score}%</div>
              </article>
            ) : (
              <p className="empty-state">Run matching to see your result.</p>
            )}
          </article>
        </section>
      )}
    </main>
  );
}

export default MatchingPage;
