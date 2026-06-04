function FormMessage({ type = 'info', children }) {
  if (!children) return null;
  return <div className={`form-message ${type}`}>{children}</div>;
}

export default FormMessage;
