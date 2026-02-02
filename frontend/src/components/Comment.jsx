import { useState } from 'react';

function Comment({ comment, onReply, onLike, user, depth = 0 }) {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmitReply = async (e) => {
    e.preventDefault();
    if (!replyContent.trim()) return;
    
    setSubmitting(true);
    try {
      await onReply(comment.id, replyContent);
      setReplyContent('');
      setShowReplyForm(false);
    } catch (err) {
      console.error('Failed to submit reply:', err);
    } finally {
      setSubmitting(false);
    }
  };

  // Limit nesting depth visually
  const marginLeft = Math.min(depth * 20, 60);

  return (
    <div style={{ marginLeft: `${marginLeft}px` }}>
      <div className="bg-sand-50 border border-sand-200 rounded p-3">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium text-sand-800 text-sm">{comment.author.username}</span>
          <span className="text-sand-400 text-xs">
            {new Date(comment.created_at).toLocaleDateString()}
          </span>
        </div>
        
        <p className="text-sand-700 text-sm mb-2 whitespace-pre-wrap">{comment.content}</p>
        
        <div className="flex items-center gap-3 text-xs">
          <button
            onClick={() => onLike(comment.id, comment.is_liked)}
            disabled={!user}
            className={`${
              comment.is_liked ? 'text-sand-800 font-medium' : 'text-sand-500'
            } hover:text-sand-700 disabled:cursor-not-allowed`}
          >
            {comment.is_liked ? 'Liked' : 'Like'} ({comment.like_count})
          </button>
          
          {user && (
            <button
              onClick={() => setShowReplyForm(!showReplyForm)}
              className="text-sand-500 hover:text-sand-700"
            >
              Reply
            </button>
          )}
        </div>
        
        {showReplyForm && (
          <form onSubmit={handleSubmitReply} className="mt-3">
            <textarea
              value={replyContent}
              onChange={(e) => setReplyContent(e.target.value)}
              placeholder="Write a reply..."
              className="w-full px-2 py-1.5 border border-sand-300 rounded text-sm resize-none focus:outline-none focus:border-sand-500"
              rows={2}
            />
            <div className="mt-1 flex gap-2 justify-end">
              <button
                type="button"
                onClick={() => setShowReplyForm(false)}
                className="px-2 py-1 text-sand-500 hover:text-sand-700 text-xs"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting || !replyContent.trim()}
                className="px-2 py-1 bg-sand-700 text-sand-50 rounded text-xs hover:bg-sand-600 disabled:opacity-50"
              >
                {submitting ? 'Posting...' : 'Reply'}
              </button>
            </div>
          </form>
        )}
      </div>
      
      {/* Render nested replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="mt-2 space-y-2">
          {comment.replies.map((reply) => (
            <Comment
              key={reply.id}
              comment={reply}
              onReply={onReply}
              onLike={onLike}
              user={user}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default Comment;
