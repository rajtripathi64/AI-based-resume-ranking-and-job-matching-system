import { Link } from 'react-router-dom';
import { BrainCircuit } from 'lucide-react';

function AuthLayout({ title, subtitle, children, footerText, footerLink, footerLinkText }) {
  return (
    <main className="auth-page">
      <section className="auth-brand-panel" aria-label="Project overview">
        <div className="brand-mark">
          <BrainCircuit size={28} />
        </div>
        <p className="eyebrow">ResumeMatch AI</p>
        <h1>AI resume screening for faster, fairer shortlisting.</h1>
      </section>

      <section className="auth-form-panel" aria-label={title}>
        <div className="auth-card">
          <p className="eyebrow">Portal Access</p>
          <h2>{title}</h2>
          <p className="form-subtitle">{subtitle}</p>
          {children}
          <p className="form-footer">
            {footerText} <Link to={footerLink}>{footerLinkText}</Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default AuthLayout;
