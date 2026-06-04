import { Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import ResumeUploadPage from './pages/ResumeUploadPage.jsx';
import JobManagementPage from './pages/JobManagementPage.jsx';
import MatchingPage from './pages/MatchingPage.jsx';
import ModelAnalysisPage from './pages/ModelAnalysisPage.jsx';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/dashboard/:role" element={<DashboardPage />} />
      <Route path="/resumes/upload" element={<ResumeUploadPage />} />
      <Route path="/jobs/manage" element={<JobManagementPage />} />
      <Route path="/matching" element={<MatchingPage />} />
      <Route path="/ml/analysis" element={<ModelAnalysisPage />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

export default App;

