import { useState, useEffect } from 'react';
import * as api from '../api';

function Leaderboard() {
  const [leaders, setLeaders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
    // Refresh every 30 seconds
    const interval = setInterval(loadLeaderboard, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadLeaderboard = async () => {
    try {
      const res = await api.getLeaderboard();
      setLeaders(res.data);
    } catch (err) {
      console.error('Failed to load leaderboard:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-sand-200 rounded-lg p-4">
      <h2 className="text-sm font-semibold text-sand-800 mb-3 uppercase tracking-wide">
        Top Contributors
      </h2>
      <p className="text-xs text-sand-500 mb-4">Last 24 hours</p>

      {loading ? (
        <p className="text-sand-500 text-sm">Loading...</p>
      ) : leaders.length === 0 ? (
        <p className="text-sand-500 text-sm">No activity yet.</p>
      ) : (
        <ol className="space-y-2">
          {leaders.map((leader) => (
            <li key={leader.id} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sand-400 text-sm w-4">{leader.rank}.</span>
                <span className="text-sand-700 text-sm">{leader.username}</span>
              </div>
              <span className="text-sand-500 text-sm">{leader.karma_24h} karma</span>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

export default Leaderboard;
