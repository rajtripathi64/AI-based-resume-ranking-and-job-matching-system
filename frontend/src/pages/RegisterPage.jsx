import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UserPlus } from 'lucide-react';
import AuthLayout from '../components/AuthLayout.jsx';
import FormMessage from '../components/FormMessage.jsx';
import { registerUser } from '../services/api.js';
import { saveSession } from '../services/session.js';

const roles = [
  { value: 'candidate', label: 'Candidate' },
  { value: 'company', label: 'Company' },
];

function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: '',
    password: '',
    role: 'candidate',
    full_name: '',
    company_name: '',
  });
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  function updateField(event) {
    setForm({ ...form, [event.target.name]: event.target.value });
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setMessage('');

    const payload = {
      email: form.email,
      password: form.password,
      role: form.role,
    };

    if (form.role === 'candidate') payload.full_name = form.full_name;
    if (form.role === 'company') payload.company_name = form.company_name;

    try {
      const data = await registerUser(payload);
      saveSession(data);
      navigate(`/dashboard/${data.user.role}`);
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout
      title="Create your account"
      subtitle="Choose your role and set up access for the correct portal."
      footerText="Already registered?"
      footerLink="/login"
      footerLinkText="Login instead"
    >
      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          Role
          <select name="role" value={form.role} onChange={updateField}>
            {roles.map((role) => <option key={role.value} value={role.value}>{role.label}</option>)}
          </select>
        </label>
        {form.role === 'candidate' && (
          <label>
            Full name
            <input name="full_name" type="text" placeholder="Candidate name" value={form.full_name} onChange={updateField} required />
          </label>
        )}
        {form.role === 'company' && (
          <label>
            Company name
            <input name="company_name" type="text" placeholder="Company name" value={form.company_name} onChange={updateField} required />
          </label>
        )}
        <label>
          Email address
          <input name="email" type="email" placeholder="name@example.com" value={form.email} onChange={updateField} required />
        </label>
        <label>
          Password
          <input name="password" type="password" placeholder="Minimum 6 characters" value={form.password} onChange={updateField} minLength="6" required />
        </label>
        <FormMessage type="error">{message}</FormMessage>
        <button className="primary-action" type="submit" disabled={loading}>
          <UserPlus size={18} /> {loading ? 'Creating...' : 'Create account'}
        </button>
      </form>
    </AuthLayout>
  );
}

export default RegisterPage;

