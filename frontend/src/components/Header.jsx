import { Link } from 'react-router-dom';
import { useAuth } from '../App';

function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-sand-200">
      <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="text-xl font-semibold text-sand-800 hover:text-sand-600">
          Playto
        </Link>
        
        <nav className="flex items-center gap-4">
          {user ? (
            <>
              <span className="text-sand-600 text-sm">
                {user.username}
              </span>
              <button
                onClick={logout}
                className="text-sm text-sand-500 hover:text-sand-700"
              >
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="text-sm text-sand-600 hover:text-sand-800"
              >
                Sign in
              </Link>
              <Link
                to="/register"
                className="text-sm px-3 py-1.5 bg-sand-800 text-sand-50 rounded hover:bg-sand-700"
              >
                Register
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}

export default Header;
