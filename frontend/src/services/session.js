export function saveSession(authData) {
  localStorage.setItem('resume_match_token', authData.access_token);
  localStorage.setItem('resume_match_user', JSON.stringify(authData.user));
}

export function getSavedUser() {
  const rawUser = localStorage.getItem('resume_match_user');
  return rawUser ? JSON.parse(rawUser) : null;
}

export function getSavedToken() {
  return localStorage.getItem('resume_match_token');
}

export function clearSession() {
  localStorage.removeItem('resume_match_token');
  localStorage.removeItem('resume_match_user');
}
