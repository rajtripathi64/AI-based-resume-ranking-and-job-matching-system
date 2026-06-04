import { useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  BarChart3,
  BriefcaseBusiness,
  Building2,
  FileText,
  LayoutDashboard,
  LogOut,
  Shield,
  Sparkles,
  UploadCloud,
  Users,
} from 'lucide-react';
import { clearSession, getSavedUser } from '../services/session.js';

const roleContent = {
  candidate: {
    title: 'Candidate Dashboard',
    subtitle: 'Upload your resume, compare it with a job description, and review your match score.',
    badge: 'Candidate Portal',
    primaryAction: { label: 'Upload Resume', href: '/resumes/upload', icon: UploadCloud },
    secondaryAction: { label: 'Check Match', href: '/matching', icon: Sparkles },
    cards: [
      { label: 'Resume Upload', text: 'Add PDF, DOCX, or TXT resume files for parsing.', icon: FileText },
      { label: 'JD Matching', text: 'Compare your resume with a company job description.', icon: Sparkles },
      { label: 'Profile Access', text: 'Your candidate portal stays separate from recruiter tools.', icon: Shield },
    ],
  },
  company: {
    title: 'Recruiter Dashboard',
    subtitle: 'Create job descriptions, upload candidate resumes, and view ranked shortlists.',
    badge: 'Recruiter Portal',
    primaryAction: { label: 'Open Matching', href: '/matching', icon: Users },
    secondaryAction: { label: 'Manage Jobs', href: '/jobs/manage', icon: BriefcaseBusiness },
    cards: [
      { label: 'Job Descriptions', text: 'Create and manage the requirements for each role.', icon: BriefcaseBusiness },
      { label: 'Bulk Resume Ranking', text: 'Upload multiple resumes and sort candidates by fit.', icon: Users },
      { label: 'Hybrid Score', text: 'Required skills, SBERT, XGBoost, and resume quality are combined.', icon: Sparkles },
    ],
  },
  admin: {
    title: 'Admin Dashboard',
    subtitle: 'Manage users and review the final ML model comparison for the system.',
    badge: 'Admin Portal',
    primaryAction: { label: 'ML Analysis', href: '/ml/analysis', icon: BarChart3 },
    secondaryAction: { label: 'Matching', href: '/matching', icon: Sparkles },
    cards: [
      { label: 'Users', text: 'Candidate, recruiter, and admin accounts use role-based access.', icon: Users },
      { label: 'Model Analysis', text: 'View training results for XGBoost and comparison models.', icon: BarChart3 },
      { label: 'Security', text: 'JWT authentication protects portal access.', icon: Shield },
    ],
  },
};

function DashboardPage() {
  const { role = 'candidate' } = useParams();
  const navigate = useNavigate();
  const user = getSavedUser();
  const content = roleContent[role] || roleContent.candidate;

  const navItems = useMemo(() => {
    const items = [
      { label: 'Overview', icon: LayoutDashboard, active: true },
      { label: 'Matching', icon: Sparkles, href: '/matching' },
    ];

    if (role === 'candidate') {
      items.splice(1, 0, { label: 'Resume', icon: FileText, href: '/resumes/upload' });
    }

    if (role === 'company') {
      items.splice(1, 0, { label: 'Jobs', icon: BriefcaseBusiness, href: '/jobs/manage' });
    }

    if (role === 'admin') {
      items.push({ label: 'ML Analysis', icon: BarChart3, href: '/ml/analysis' });
    }

    return items;
  }, [role]);

  function handleLogout() {
    clearSession();
    navigate('/login');
  }

  const PrimaryIcon = content.primaryAction.icon;
  const SecondaryIcon = content.secondaryAction.icon;

  return (
    <main className="dashboard-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-mark small"><Sparkles size={22} /></div>
          <div>
            <strong>ResumeMatch</strong>
            <span>AI Screening</span>
          </div>
        </div>
        <nav className="sidebar-nav" aria-label="Dashboard navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button className={item.active ? 'nav-item active' : 'nav-item'} key={item.label} type="button" onClick={() => item.href && navigate(item.href)}>
                <Icon size={18} /> {item.label}
              </button>
            );
          })}
        </nav>
        <button className="logout-button" type="button" onClick={handleLogout}>
          <LogOut size={18} /> Logout
        </button>
      </aside>

      <section className="dashboard-main simplified-dashboard">
        <header className="dashboard-header compact">
          <div>
            <p className="dashboard-badge">{content.badge}</p>
            <h1>{content.title}</h1>
            <p>{content.subtitle}</p>
          </div>
          <div className="user-chip">
            <span>{user?.email || `${role}@example.com`}</span>
            <strong>{user?.role || role}</strong>
          </div>
        </header>

        <section className="quick-actions" aria-label="Primary dashboard actions">
          <button className="primary-action" type="button" onClick={() => navigate(content.primaryAction.href)}>
            <PrimaryIcon size={18} /> {content.primaryAction.label}
          </button>
          <button className="secondary-action" type="button" onClick={() => navigate(content.secondaryAction.href)}>
            <SecondaryIcon size={18} /> {content.secondaryAction.label}
          </button>
        </section>

        <section className="portal-card-grid" aria-label="Portal tools">
          {content.cards.map((card) => {
            const Icon = card.icon;
            return (
              <article className="portal-card" key={card.label}>
                <div className="metric-icon"><Icon size={20} /></div>
                <strong>{card.label}</strong>
                <p>{card.text}</p>
              </article>
            );
          })}
        </section>
      </section>
    </main>
  );
}

export default DashboardPage;
