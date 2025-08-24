from posts.models import Post


def get_post_by_chapter(chapter_id):
    return Post.objects.filter(chapter_id=chapter_id)