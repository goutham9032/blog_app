# Python imports
import time
import os
import json

# Django imports
from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# User imports
from app.models import BlogPost, BlogComments, UserLikes

log = settings.LOG

@login_required
def view_edit_blog(request, slug, type):
    '''
    This function returns view/edit blog page
    params:
        slug : str - slug(id) of the blog
        type : str - page type (view/edit)
    '''
    cmnts = lambda x:BlogComments.objects.filter(blogpost=x)
    blogs = BlogPost.objects.filter(slug=int(slug))
    if type == 'view':
       posts = [dict(blog=blog, comments=cmnts(blog)) for blog in blogs]
       return render(request, 'view_edit_blog.html', {'feeds':posts})
    elif type == 'edit' and request.user == blogs.first().owner or request.user.useraddinfo.active:
       return render(request, 'view_edit_blog.html', {'feed':blogs.first()})
    else:
       return render(request, 'error.html')
     
@csrf_exempt
def blog_activity(request):
    '''
    This function will handle activities related to blog like delete/unlike/like of the blog 
    and return json response
    '''

    body = json.loads(request.body.decode())
    feed_id = int(body['feed_id'])
    feed = BlogPost.objects.get(slug=feed_id)

    if body.get('action') == 'like':
       likes = feed.likes_count + 1
       BlogPost.objects.filter(slug=feed_id).update(likes_count=likes)
       UserLikes.objects.create(blog=feed, user=request.user)
       return JsonResponse({'success':True, 'likes':likes})
    elif body.get('action') == 'unlike':
       likes = feed.likes_count - 1
       BlogPost.objects.filter(slug=feed_id).update(likes_count=likes)
       UserLikes.objects.filter(blog=feed, user=request.user).delete()
       return JsonResponse({'success':True, 'likes':likes})
    elif body.get('action') == 'delete':
       try:
          feed.delete()
          if feed.file_location:
              os.remove(base_dir + feed.file_location)
          return JsonResponse({'success':True})
       except:
          return JsonResponse({'success':False})
    elif body.get('action') == 'update':
       BlogPost.objects.filter(slug=int(body['feed_id'])).update(description=body['desc'])
       return JsonResponse({'success':True, })

def post_feed(request):
    '''
    This function will create an blog with suitable data in the database and return OK
    '''
    desc = request.GET.get('desc','')
    action = request.GET.get('action','')
    uploaded_file_url = ''
    if request.method == 'POST' and request.FILES.get('myfile',''):
        # TODO: There is some problem in frontend while loading file 
        # so storing file logic is inactive
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
    BlogPost.objects.create(file_location=uploaded_file_url,
                                slug=int(time.time()),
                                owner=request.user,
                                description=desc)
    return HttpResponse('OK')

@csrf_exempt
def create_comment(request):
    '''
    This function will create comment for an blog and store in database
    '''
    req_body = json.loads(request.body.decode())
    blog = BlogPost.objects.get(slug=req_body['blog_id'])
    try:
       cmnt = BlogComments.objects.create(comment_creator=request.user, 
                   blogpost=blog, comment=req_body['comment'])
       data = dict(success=True, username=request.user.username, 
                   cmnt_id=cmnt.slug, avatar=request.user.useraddinfo.avatar,
                   firstname=request.user.first_name)
       return JsonResponse(data) 
    except:
       return JsonResponse({'success':False}) 

def login_user(request):
    '''
    This function will opens login page and authenticate user based on login details 
    '''
    if request.method == 'POST':
        req = request.POST.dict()
        username = req.get('username','')
        password = req.get('password','')
        if not (User.objects.filter(username=username).exists() and password):
            return render(request, 'registration/login.html', {'success': False, 'data':req})
        user = authenticate(username = username, password = password)
        if user and not user.useraddinfo.active:
           return render(request, 'registration/login.html', {'disabled': True,'data':req, 'success':True})
        if not user:
            return render(request, 'registration/login.html', {'success': False, 'data':req})
        login(request, user)
        return HttpResponseRedirect('/')
    else:
        return render(request, 'registration/login.html', {'success': True})

def logout_user(request):
    '''
    This function will logout user 
    '''
    logout(request)
    return HttpResponseRedirect('/')

def register(request):
    '''
    This function will open signup page and take required user info and create user in database and 
    redirects to users home page
    '''
    if request.method == 'POST':
        post_body = request.POST.dict()
        username, email = post_body['username'], post_body['email']
        firstname, lastname = post_body['firstname'], post_body['lastname']
        password, role = post_body['password'], post_body['role']
        user_exists = User.objects.filter(username=username).exists()
        email_exists = User.objects.filter(email=email).exists()
        if not (user_exists or email_exists):
            User.objects.create_user(username=username, email=email,
                                     password=password, first_name=firstname,
                                     last_name=lastname, is_superuser=True if role=='admin' else False)
            user = authenticate(username = username, password = password)
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            context = dict(success=False, user_exists=user_exists, email_exits=email_exists, data=post_body)
            return render(request, 'registration/register.html', context)
    return render(request, 'registration/register.html', {'success':True})

@csrf_exempt
@login_required
def user_settings(request, user_type):
    '''
    This function will open users/admin settings page where he/she can open and update firstname,lastname
    and enable/disable user access to app based(Note:this is case of admin)
    '''
    non_admins = User.objects.filter(is_superuser=False)
    if request.method == 'GET':
       return render(request, 'settings.html', {'non_admins':non_admins})
    body = json.loads(request.body.decode())
    if body['action'] == 'update':
       User.objects.filter(id=request.user.id).update(first_name=body['firstname'],last_name=body['lastname'])
       return JsonResponse({'success':True})
    elif body['action'] == 'change':
       status = False if body['status'] == 'disable' else True
       user = User.objects.filter(id=body['user_id']).first()
       user.useraddinfo.active = status
       user.save()
       return JsonResponse({'success':True})
 
def get_paginated_blogs(blogs_list, request, per_page=1):
    '''
    This function will paginate query results and return paginated objects
    '''
    cmnts = lambda x:BlogComments.objects.filter(blogpost=x)
    liked = lambda x,y:UserLikes.objects.filter(user=x, blog=y).exists()
    posts_list = [dict(blog=blog, comments=cmnts(blog), liked=liked(request.user, blog)) for blog in blogs_list]
    page = request.GET.get('page', 1)
    paginator = Paginator(posts_list, per_page)
    try:
        blogs = paginator.page(page)
    except PageNotAnInteger:
        blogs = paginator.page(1)
    except EmptyPage:
        blogs = paginator.page(paginator.num_pages)
    return blogs

@login_required
def user_page(request, username):
    '''
    This function will open user page and show only the feeds that was owned by specific user
    '''
    if username == request.user.username:
       return HttpResponseRedirect('/')
    user = User.objects.filter(username=username).first()
    blogs_list = BlogPost.objects.filter(owner=user).order_by('-updated_at')
    blogs = get_paginated_blogs(blogs_list, request, 10) 
    return render(request, 'home.html', {'feeds':blogs})

@login_required
def home(request):
    '''
    This function will opens users home page
    '''
    blogs_list = BlogPost.objects.all().order_by('-updated_at')
    blogs = get_paginated_blogs(blogs_list, request) 
    return render(request, 'home.html', {'feeds':blogs})

