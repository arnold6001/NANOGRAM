# apps/hashtags/models.py
class Hashtag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    posts = models.ManyToManyField('posts.Post', related_name='hashtags')

# Extract on save
@receiver(post_save, sender=Post)
def extract_hashtags(sender, instance, **kwargs):
    import re
    tags = set(re.findall(r'#(\w+)', instance.caption))
    for t in tags:
        ht, _ = Hashtag.objects.get_or_create(name=t.lower())
        ht.posts.add(instance)

# Explore view (top 9 trending hashtags + recent popular posts)
class ExploreViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostSerializer
    def get_queryset(self):
        trending = Hashtag.objects.annotate(pc=models.Count('posts')).order_by('-pc')[:9]
        post_ids = Post.objects.filter(hashtags__in=trending).values_list('id', flat=True)
        return Post.objects.filter(id__in=post_ids).order_by('-like_count')[:30]