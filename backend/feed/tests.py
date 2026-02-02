from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from .models import Post, Comment, PostLike, CommentLike, KarmaTransaction


class LeaderboardTestCase(TestCase):
    """
    Test the 24-hour rolling leaderboard calculation.
    This verifies that only karma earned in the last 24 hours is counted.
    """

    def setUp(self):
        self.client = APIClient()
        
        # Create test users
        self.user1 = User.objects.create_user('alice', password='pass123')
        self.user2 = User.objects.create_user('bob', password='pass123')
        self.user3 = User.objects.create_user('charlie', password='pass123')
        
        # Create a post by user1
        self.post = Post.objects.create(author=self.user1, content='Test post')

    def test_leaderboard_only_counts_last_24_hours(self):
        """Karma older than 24 hours should not appear in leaderboard."""
        
        # Give user1 karma from 2 days ago (should NOT count)
        old_karma = KarmaTransaction.objects.create(
            user=self.user1,
            karma_type='post_like',
            points=5
        )
        # Manually set created_at to 2 days ago
        old_karma.created_at = timezone.now() - timedelta(days=2)
        old_karma.save(update_fields=['created_at'])
        
        # Give user2 karma from 1 hour ago (should count)
        recent_karma = KarmaTransaction.objects.create(
            user=self.user2,
            karma_type='post_like',
            points=5
        )
        
        # Get leaderboard
        response = self.client.get('/api/leaderboard/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        
        # user2 should be on leaderboard, user1 should not
        usernames = [entry['username'] for entry in data]
        self.assertIn('bob', usernames)
        self.assertNotIn('alice', usernames)

    def test_leaderboard_ranks_correctly(self):
        """Users should be ranked by karma amount descending."""
        
        # user1 gets 10 karma
        KarmaTransaction.objects.create(user=self.user1, karma_type='post_like', points=5)
        KarmaTransaction.objects.create(user=self.user1, karma_type='post_like', points=5)
        
        # user2 gets 15 karma
        KarmaTransaction.objects.create(user=self.user2, karma_type='post_like', points=5)
        KarmaTransaction.objects.create(user=self.user2, karma_type='post_like', points=5)
        KarmaTransaction.objects.create(user=self.user2, karma_type='post_like', points=5)
        
        # user3 gets 1 karma
        KarmaTransaction.objects.create(user=self.user3, karma_type='comment_like', points=1)
        
        response = self.client.get('/api/leaderboard/')
        data = response.json()
        
        # Check ranking order
        self.assertEqual(data[0]['username'], 'bob')
        self.assertEqual(data[0]['karma_24h'], 15)
        self.assertEqual(data[0]['rank'], 1)
        
        self.assertEqual(data[1]['username'], 'alice')
        self.assertEqual(data[1]['karma_24h'], 10)
        self.assertEqual(data[1]['rank'], 2)
        
        self.assertEqual(data[2]['username'], 'charlie')
        self.assertEqual(data[2]['karma_24h'], 1)
        self.assertEqual(data[2]['rank'], 3)

    def test_leaderboard_limits_to_5(self):
        """Leaderboard should only show top 5 users."""
        
        # Create 7 users with karma
        for i in range(7):
            user = User.objects.create_user(f'user{i}', password='pass')
            KarmaTransaction.objects.create(
                user=user,
                karma_type='post_like',
                points=10 - i  # Decreasing karma
            )
        
        response = self.client.get('/api/leaderboard/')
        data = response.json()
        
        self.assertEqual(len(data), 5)
        self.assertEqual(data[0]['username'], 'user0')
        self.assertEqual(data[4]['username'], 'user4')


class LikeRaceConditionTestCase(TestCase):
    """
    Test that the unique constraint prevents double-liking.
    """

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='pass123')
        self.author = User.objects.create_user('author', password='pass123')
        self.post = Post.objects.create(author=self.author, content='Test post')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_cannot_double_like_post(self):
        """Liking the same post twice should fail."""
        
        # First like should succeed
        response1 = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response1.status_code, 200)
        
        # Second like should fail
        response2 = self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(response2.status_code, 400)
        
        # Should only have one like
        self.assertEqual(PostLike.objects.filter(user=self.user, post=self.post).count(), 1)
        
        # Should only have one karma transaction
        self.assertEqual(KarmaTransaction.objects.filter(user=self.author).count(), 1)

    def test_unlike_removes_karma(self):
        """Unliking should remove the karma transaction."""
        
        # Like the post
        self.client.post(f'/api/posts/{self.post.id}/like/')
        self.assertEqual(KarmaTransaction.objects.filter(user=self.author).count(), 1)
        
        # Unlike the post
        response = self.client.post(f'/api/posts/{self.post.id}/unlike/')
        self.assertEqual(response.status_code, 200)
        
        # Karma transaction should be deleted
        self.assertEqual(KarmaTransaction.objects.filter(user=self.author).count(), 0)
