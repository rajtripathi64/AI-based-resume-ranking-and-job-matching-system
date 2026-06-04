import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn } from 'lucide-react';
import AuthLayout from '../components/AuthLayout.jsx';
import FormMessage from '../components/FormMessage.jsx';
import { loginUser } from '../services/api.js';
import { saveSession } from '../services/session.js';

function LoginPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const data = await loginUser(form);
      saveSession(data);
      navigate(`/dashboard/${data.user.role}`);
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Login failed. Check email and password.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Log in to continue to your role-based dashboard."
      footerText="New to the system?"
      footerLink="/register"
      footerLinkText="Create an account"
    >
      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          Email address
          <input name="email" type="email" placeholder="candidate@example.com" value={form.email} onChange={updateField} required />
        </label>
        <label>
          Password
          <input name="password" type="password" placeholder="Enter password" value={form.password} onChange={updateField} required />
        </label>
        <FormMessage type="error">{message}</FormMessage>
        <button className="primary-action" type="submit" disabled={loading}>
          <LogIn size={18} /> {loading ? 'Checking...' : 'Login'}
        </button>
      </form>
    </AuthLayout>
  );
}

export default LoginPage;
