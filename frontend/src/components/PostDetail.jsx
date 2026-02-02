import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAuth } from '../App';
import * as api from '../api';
import Comment from './Comment';

function PostDetail() {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [newComment, setNewComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    loadPost();
  }, [id]);

  const loadPost = async () => {
    try {
      const res = await api.getPost(id);
      setPost(res.data);
    } catch (err) {
      console.error('Failed to load post:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLikePost = async () => {
    if (!user) return;
    try {
      if (post.is_liked) {
        await api.unlikePost(id);
      } else {
        await api.likePost(id);
      }
      loadPost();
    } catch (err) {
      console.error('Failed to toggle like:', err);
    }
  };

  const handleSubmitComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    
    setSubmitting(true);
    try {
      await api.createComment(id, newComment);
      setNewComment('');
      loadPost();
    } catch (err) {
      console.error('Failed to create comment:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleReply = async (parentId, content) => {
    try {
      await api.createComment(id, content, parentId);
      loadPost();
    } catch (err) {
      console.error('Failed to create reply:', err);
    }
  };

  const handleLikeComment = async (commentId, isLiked) => {
    try {
      if (isLiked) {
        await api.unlikeComment(commentId);
      } else {
        await api.likeComment(commentId);
      }
      loadPost();
    } catch (err) {
      console.error('Failed to toggle comment like:', err);
    }
  };

  if (loading) {
    return <p className="text-sand-500">Loading...</p>;
  }

  if (!post) {
    return <p className="text-sand-500">Post not found.</p>;
  }

  return (
    <div>
      <Link to="/" className="text-sand-500 hover:text-sand-700 text-sm mb-4 inline-block">
        Back to feed
      </Link>

      <article className="bg-white border border-sand-200 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2 mb-2">
          <span className="font-medium text-sand-800">{post.author.username}</span>
          <span className="text-sand-400 text-sm">
            {new Date(post.created_at).toLocaleDateString()}
          </span>
        </div>
        
        <p className="text-sand-700 mb-3 whitespace-pre-wrap">{post.content}</p>
        
        <div className="flex items-center gap-4 text-sm">
          <button
            onClick={handleLikePost}
            disabled={!user}
            className={`flex items-center gap-1 ${
              post.is_liked ? 'text-sand-800 font-medium' : 'text-sand-500'
            } hover:text-sand-700 disabled:cursor-not-allowed`}
          >
            <span>{post.is_liked ? 'Liked' : 'Like'}</span>
            <span>({post.like_count})</span>
          </button>
        </div>
      </article>

      <section>
        <h2 className="text-lg font-medium text-sand-800 mb-4">Comments</h2>
        
        {user && (
          <form onSubmit={handleSubmitComment} className="mb-6">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Write a comment..."
              className="w-full px-3 py-2 border border-sand-300 rounded resize-none focus:outline-none focus:border-sand-500"
              rows={2}
            />
            <div className="mt-2 flex justify-end">
              <button
                type="submit"
                disabled={submitting || !newComment.trim()}
                className="px-3 py-1.5 bg-sand-800 text-sand-50 rounded hover:bg-sand-700 disabled:opacity-50 text-sm"
              >
                {submitting ? 'Posting...' : 'Comment'}
              </button>
            </div>
          </form>
        )}

        {post.comments && post.comments.length > 0 ? (
          <div className="space-y-3">
            {post.comments.map((comment) => (
              <Comment
                key={comment.id}
                comment={comment}
                onReply={handleReply}
                onLike={handleLikeComment}
                user={user}
              />
            ))}
          </div>
        ) : (
          <p className="text-sand-500 text-sm">No comments yet.</p>
        )}
      </section>
    </div>
  );
}

export default PostDetail;
