# views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CommunityForumPostModel
from .serializers import CommunityForumPostSerializer

@csrf_exempt
def community_forum_posts(request, id=None):
    if request.method == 'GET':
        if id is not None:
            try:
                post = CommunityForumPostModel.objects.get(pk=id)
                serializer = CommunityForumPostSerializer(post)
                return JsonResponse(serializer.data)
            except CommunityForumPostModel.DoesNotExist:
                return JsonResponse({'error': 'Community Forum Post not found'}, status=404)
        else:
            posts = CommunityForumPostModel.objects.all()
            serializer = CommunityForumPostSerializer(posts, many=True)
            return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        serializer = CommunityForumPostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'PUT' or request.method == 'PATCH':
        data = json.loads(request.body)
        try:
            post = CommunityForumPostModel.objects.get(pk=id)
        except CommunityForumPostModel.DoesNotExist:
            return JsonResponse({'error': 'Community Forum Post not found'}, status=404)
        serializer = CommunityForumPostSerializer(post, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=200)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        try:
            post = CommunityForumPostModel.objects.get(pk=id)
            post.delete()
            return JsonResponse({'message': 'Community Forum Post deleted successfully'}, status=200)
        except CommunityForumPostModel.DoesNotExist:
            return JsonResponse({'error': 'Community Forum Post not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': f'Failed to delete community forum post: {str(e)}'}, status=500)
