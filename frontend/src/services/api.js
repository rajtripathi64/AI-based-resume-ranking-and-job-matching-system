import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
});

export async function loginUser(payload) {
  const response = await api.post('/api/auth/login', payload);
  return response.data;
}

export async function registerUser(payload) {
  const response = await api.post('/api/auth/register', payload);
  return response.data;
}

export async function getCurrentUser(token) {
  const response = await api.get('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function uploadResume(file, token) {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/resumes/upload', formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

export async function getMyResumes(token) {
  const response = await api.get('/api/resumes/mine', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function createJob(payload, token) {
  const response = await api.post('/api/jobs', payload, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function getMyJobs(token) {
  const response = await api.get('/api/jobs/mine', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function updateJob(jobId, payload, token) {
  const response = await api.put(`/api/jobs/${jobId}`, payload, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function deleteJob(jobId, token) {
  const response = await api.delete(`/api/jobs/${jobId}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export default api;

export async function uploadCompanyResume(candidateName, file, token) {
  const formData = new FormData();
  formData.append('candidate_name', candidateName);
  formData.append('file', file);
  const response = await api.post('/api/resumes/company-pool/upload', formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

export async function getCompanyResumes(token) {
  const response = await api.get('/api/resumes/company-pool', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function rankCompanyResumes(jobId, token) {
  const response = await api.post(`/api/matching/job-to-company-resumes/${jobId}`, {}, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function rankJobsForResume(resumeId, token) {
  const response = await api.post(`/api/matching/resume-to-jobs/${resumeId}`, {}, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function instantCandidateMatch({ resumeFile, jdText, jdFile }, token) {
  const formData = new FormData();
  formData.append('resume_file', resumeFile);
  if (jdText) formData.append('jd_text', jdText);
  if (jdFile) formData.append('jd_file', jdFile);
  const response = await api.post('/api/matching/instant-candidate', formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

export async function instantCompanyMatch({ candidateNames, jdText, jdFile, resumeFiles }, token) {
  const formData = new FormData();
  formData.append('candidate_names', candidateNames);
  if (jdText) formData.append('jd_text', jdText);
  if (jdFile) formData.append('jd_file', jdFile);
  resumeFiles.forEach((file) => formData.append('resume_files', file));
  const response = await api.post('/api/matching/instant-company', formData, {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}


export async function trainModels({ maxSamples = 300, threshold = 70 }, token) {
  const response = await api.post(`/api/ml/train?max_samples=${maxSamples}&threshold=${threshold}`, {}, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function getModelRuns(token) {
  const response = await api.get('/api/ml/runs', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

export async function getModelComparison(token) {
  const response = await api.get('/api/ml/comparison', {
    headers: { Authorization: `Bearer ${token}` },
  });
  return response.data;
}

