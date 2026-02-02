import { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import * as api from './api';
import Feed from './components/Feed';
import PostDetail from './components/PostDetail';
import Login from './components/Login';
import Register from './components/Register';
import Header from './components/Header';
import Leaderboard from './components/Leaderboard';

const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getCurrentUser()
      .then(res => {
        if (res.data.authenticated) {
          setUser(res.data.user);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-sand-500">Loading...</p>
      </div>
    );
  }

  return (
    <AuthContext.Provider value={{ user, setUser: handleLogin, logout: handleLogout }}>
      <BrowserRouter>
        <div className="min-h-screen bg-sand-50">
          <Header />
          <div className="max-w-6xl mx-auto px-4 py-6">
            <div className="flex gap-6">
              <main className="flex-1">
                <Routes>
                  <Route path="/" element={<Feed />} />
                  <Route path="/post/:id" element={<PostDetail />} />
                  <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
                  <Route path="/register" element={user ? <Navigate to="/" /> : <Register />} />
                </Routes>
              </main>
              <aside className="w-72 hidden lg:block">
                <Leaderboard />
              </aside>
            </div>
          </div>
        </div>
      </BrowserRouter>
    </AuthContext.Provider>
  );
}

export default App;
