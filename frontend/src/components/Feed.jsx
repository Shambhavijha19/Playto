import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../App';
import * as api from '../api';

function Feed() {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newPost, setNewPost] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    loadPosts();
  }, []);

  const loadPosts = async () => {
    try {
      const res = await api.getPosts();
      setPosts(res.data);
    } catch (err) {
      console.error('Failed to load posts:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitPost = async (e) => {
    e.preventDefault();
    if (!newPost.trim()) return;
    
    setSubmitting(true);
    try {
      await api.createPost(newPost);
      setNewPost('');
      loadPosts();
    } catch (err) {
      console.error('Failed to create post:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleLike = async (postId, isLiked) => {
    try {
      if (isLiked) {
        await api.unlikePost(postId);
      } else {
        await api.likePost(postId);
      }
      loadPosts();
    } catch (err) {
      console.error('Failed to toggle like:', err);
    }
  };

  if (loading) {
    return <p className="text-sand-500">Loading posts...</p>;
  }

  return (
    <div>
      {user && (
        <form onSubmit={handleSubmitPost} className="mb-6">
          <textarea
            value={newPost}
            onChange={(e) => setNewPost(e.target.value)}
            placeholder="What's on your mind?"
            className="w-full px-4 py-3 border border-sand-300 rounded-lg resize-none focus:outline-none focus:border-sand-500"
            rows={3}
          />
          <div className="mt-2 flex justify-end">
            <button
              type="submit"
              disabled={submitting || !newPost.trim()}
              className="px-4 py-2 bg-sand-800 text-sand-50 rounded hover:bg-sand-700 disabled:opacity-50 text-sm"
            >
              {submitting ? 'Posting...' : 'Post'}
            </button>
          </div>
        </form>
      )}

      {posts.length === 0 ? (
        <p className="text-sand-500 text-center py-8">No posts yet. Be the first to share something.</p>
      ) : (
        <div className="space-y-4">
          {posts.map((post) => (
            <article key={post.id} className="bg-white border border-sand-200 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-medium text-sand-800">{post.author.username}</span>
                <span className="text-sand-400 text-sm">
                  {new Date(post.created_at).toLocaleDateString()}
                </span>
              </div>
              
              <Link to={`/post/${post.id}`} className="block">
                <p className="text-sand-700 mb-3 whitespace-pre-wrap">{post.content}</p>
              </Link>
              
              <div className="flex items-center gap-4 text-sm">
                <button
                  onClick={() => handleLike(post.id, post.is_liked)}
                  disabled={!user}
                  className={`flex items-center gap-1 ${
                    post.is_liked ? 'text-sand-800 font-medium' : 'text-sand-500'
                  } hover:text-sand-700 disabled:cursor-not-allowed`}
                >
                  <span>{post.is_liked ? 'Liked' : 'Like'}</span>
                  <span>({post.like_count})</span>
                </button>
                
                <Link 
                  to={`/post/${post.id}`}
                  className="text-sand-500 hover:text-sand-700"
                >
                  {post.comment_count} {post.comment_count === 1 ? 'comment' : 'comments'}
                </Link>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}

export default Feed;
