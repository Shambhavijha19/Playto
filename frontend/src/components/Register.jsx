import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../App';
import * as api from '../api';

function Register() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await api.register(username, password);
      setUser(res.data.user);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-sm mx-auto mt-12">
      <h1 className="text-2xl font-semibold text-sand-800 mb-6">Create account</h1>
      
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm text-sand-700 mb-1">Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-3 py-2 border border-sand-300 rounded focus:outline-none focus:border-sand-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm text-sand-700 mb-1">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border border-sand-300 rounded focus:outline-none focus:border-sand-500"
            minLength={4}
            required
          />
          <p className="text-xs text-sand-500 mt-1">At least 4 characters</p>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 bg-sand-800 text-sand-50 rounded hover:bg-sand-700 disabled:opacity-50"
        >
          {loading ? 'Creating account...' : 'Create account'}
        </button>
      </form>

      <p className="mt-4 text-sm text-sand-600 text-center">
        Already have an account?{' '}
        <Link to="/login" className="text-sand-800 hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}

export default Register;
