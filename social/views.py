import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import User
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from social.models import UserProfile, UserPost, FriendRequest
from datetime import datetime
from django.utils import timezone
from django.contrib import messages
from .forms import UserProfileForm
from .forms import UserPostForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


# def get_data(request):
#     users = User.objects.all()
#
#     data = []
#     for user in users:
#         data.append({
#             'name': user.username,
#             'id': user.id,
#         })
#     return HttpResponse(json.dumps(data), content_type='application/json')
#

def logout_user(request):
    logout(request)
    return redirect('login')


def count_friend_requests_sent(request):
    logged_user = UserProfile.objects.get(user=request.user)
    friend_requests_sent = FriendRequest.objects.filter(from_user=logged_user)
    friend_requests_sent = reversed(friend_requests_sent)
    return render(request, 'count_friend_requests.html', {'friend_requests_sent': friend_requests_sent})


@login_required
def unfriend(request, username):
    user_profile = UserProfile.objects.get(user=request.user)
    friend_to_unfriend = UserProfile.objects.get(user__username=username)

    user_profile.friends.remove(friend_to_unfriend)

    return redirect('/displayProfile')


def create_post(request):
    if request.method == 'POST':
        form = UserPostForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = request.user.userprofile
            new_post = form.save(commit=False)
            new_post.username = user_profile
            new_post.save()
            return redirect('/display_posts')  # Redirect to a page that displays all posts after successful submission
    else:
        form = UserPostForm()
    return render(request, 'create_post.html', {'form': form})


def display_posts(request, user_id = None):
    user = request.user
    if user_id is None:
        all_posts = UserPost.objects.filter(username__user=user)
        user_view = request.user.username
    else:
        all_posts = UserPost.objects.filter(username_id=user_id)
        curr = UserProfile.objects.get(pk=user_id)
        user_view = curr.user.username
    all_posts = reversed(all_posts)
    if request.method == 'POST':
        post_id_to_delete = request.POST.get('post_id_to_delete')
        if post_id_to_delete:
            # Delete the post if the logged-in user is the owner of the post
            post_to_delete = get_object_or_404(UserPost, id=post_id_to_delete, username__user=user)
            post_to_delete.delete()
            return redirect('display_posts')
    return render(request, 'display_posts.html', {'all_posts': all_posts, 'user_view': user_view})


def upload_profile_image(request, username = None):
    user, created = User.objects.get_or_create(username=username)
    visible = True
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile(user=user)
        visible = False

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('display_profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'upload_profile_image.html', {'form': form, 'visible': visible})


def index(request):
    return render(request, "index.html")


def any_profile_view(request, user_id=None):
    print(type(user_id), user_id)
    # user_id = int(user_id)
    print(request.user)
    user = get_object_or_404(UserProfile, pk=user_id)
    user_posts = UserPost.objects.filter(username=user).count()
    users = UserProfile.objects.all().exclude(user=request.user)
    # print(users)
    curr_user = UserProfile.objects.get(user=request.user)
    all_friends = curr_user.friends.all()
    req_from = UserProfile.objects.get(user=request.user)
    all_req = FriendRequest.objects.filter(from_user=req_from)
    only_to_user = [req.to_user for req in all_req]
    res_query = list(all_friends) + list(only_to_user)

    res = False
    curr_search = ""
    user_idd = ""
    if request.method == 'POST':
        curr_search = request.POST.get('searchForm')
        if request.POST.get('searchForm'):
            try:
                user_u = User.objects.get(username=curr_search)
                user_pro = UserProfile.objects.get(user=user_u)
                user_idd = user_pro.id
            except User.DoesNotExist or UserProfile.DoesNotExist:
                user_idd = None
            for s_user in users:
                temp = str(s_user.user)
                if temp == curr_search:
                    res = True
                    break
                else:
                    res = False
            if not res:
                curr_search = "User Not Found"
        elif user_posts > 0 and request.POST.get('all'):
            return redirect(f'/display_posts/{user_id}')

        elif request.POST.get('add_button'):
            selected_user = request.POST.get('add_button')
            print(selected_user, "sel")

            user = User.objects.get(username=selected_user)
            user_profile = UserProfile.objects.get(user=user)
            print(user, user_profile)
            user_id = user_profile.pk
            print(user_id)
            to_user = UserProfile.objects.get(pk=user_id)
            from_user = UserProfile.objects.get(user=request.user)
            existing_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).first()

            # Check if users are already friends
            if from_user.friends.filter(pk=user_id).exists():
                messages.warning(request, f'You are already friends with {to_user.user}.')
                return redirect('/displayProfile')

            # Check if a friend request already exists
            elif existing_request:
                messages.warning(request, 'Request is already sent.')
                return redirect('/displayProfile')
            else:
                messages.success(request, 'Request sent.')
                return redirect(f'/send_friend_request/{user_id}/')

    context = {
        'user_profile': user,
        'all_user': users,
        'all_post': user_posts,
        'found': res,
        'search': curr_search,
        'user_id': user_idd,
        'disable': True,
        'isSent': False,
        'sugg': True,
        'isFriend': res_query,
        'isHome': True,
        'myProfile': "User"
    }
    return render(request, 'displayProfile.html', context)


@login_required
def send_friend_request(request, user_id):
    to_user = UserProfile.objects.get(pk=user_id)
    from_user = UserProfile.objects.get(user=request.user)

    friend_request = FriendRequest(from_user=from_user, to_user=to_user)
    friend_request.save()
    # return redirect(f'/any_profile_view/{user_id}')
    return redirect('/displayProfile')


@login_required
def received_friend_requests(request):
    logged_user = UserProfile.objects.get(user=request.user)
    received_requests = FriendRequest.objects.filter(to_user=logged_user)
    return render(request, 'received_requests.html', {'received_requests': received_requests})


def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, pk=request_id)
    logged_user = UserProfile.objects.get(user=request.user)

    if logged_user == friend_request.to_user:
        friend_request.delete()
        messages.success(request, f'Friend request from {friend_request.from_user.user.username} has been rejected.')

    return redirect('display_profile')


@login_required
def accept_friend_request(request, request_id):
    # print("accept")
    friend_request = get_object_or_404(FriendRequest, pk=request_id)
    logged_user = UserProfile.objects.get(user=request.user)

    if logged_user == friend_request.to_user:
        friend_request.from_user.friends.add(friend_request.to_user)
        friend_request.to_user.friends.add(friend_request.from_user)

        friend_request.delete()
    return redirect('friend_requests')


@login_required
def all_user_posts(request, user_id = None):
    # print(user_id)
    user = request.user
    date = timezone.now().date()
    if user_id is None:
        user_all_posts = UserPost.objects.filter(username__user=user)
    else:
        user_all_posts = UserPost.objects.filter(username_id=user_id)

    user_all_posts = reversed(user_all_posts)  # to display posts in latest order of addition
    return render(request, "allPosts.html", {'user_all_posts': user_all_posts, 'user': user, 'date': date})


def start_post(request):
    username = request.user
    date = timezone.now().date()
    time = timezone.now().time()
    user_profile = UserProfile.objects.get(user=username)

    if request.method == 'POST':
        caption = request.POST.get('caption')
        file = request.POST.get('post_file')

        # print(date, " ", time, username)
        newpost = UserPost()
        newpost.username = user_profile
        newpost.date = date
        newpost.time = time
        newpost.caption = caption
        newpost.files = file

        newpost.save()
        return redirect('/userPost')

    context = {
        'username': username,
    }
    return render(request, "createPost.html", context)


def friends_list(request):
    user_profile = UserProfile.objects.get(user=request.user)
    friends = user_profile.friends.all()
    return render(request, 'friendList.html', {'friends': friends})


# @login_required
def display_profile(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return render(request, 'upload_profile_image.html', {'error': True})

    users = UserProfile.objects.all().exclude(user=request.user)

    curr_user = request.user
    totalPost = UserPost.objects.filter(username__user=curr_user).count()
    logged_user = UserProfile.objects.get(user=request.user)
    pending_requests_count = FriendRequest.objects.filter(to_user=logged_user).count()
    friends = logged_user.friends.all().count()
    sent_request = FriendRequest.objects.filter(from_user=logged_user).count()

    # curr_user = UserProfile.objects.get(user=request.user)
    all_friends = logged_user.friends.all()
    req_from = UserProfile.objects.get(user=request.user)
    all_req = FriendRequest.objects.filter(from_user=req_from)
    only_to_user = [req.to_user for req in all_req]
    res_query = list(all_friends) + list(only_to_user)

    # sugg_friends = logged_user.friends.all()

    # print(sent_request,"sent")
    res = False
    curr_search = ""
    user_idd = ""

    if request.method == 'POST':
        # import ipdb
        # ipdb.set_trace()
        curr_search = request.POST.get('searchForm')

        if totalPost > 0 and request.POST.get('all'):
            return redirect('/display_posts')

        elif pending_requests_count > 0 and request.POST.get('friend_requests'):
            return redirect('/friend_requests')

        # adding friend part will come here
        elif request.POST.get('selected_user_id') or request.POST.get('add_button'):
            if request.POST.get('selected_user_id'):
                selected_user = request.POST.get('selected_user_id')
                # print(selected_user, "sel")
            else:
                selected_user = request.POST.get('add_button')

            sel_user = User.objects.get(username=selected_user)
            sel_user_profile = UserProfile.objects.get(user=sel_user)
            print(sel_user, sel_user_profile)
            sel_user_id = sel_user_profile.pk
            print(sel_user_id)
            to_user = UserProfile.objects.get(pk=sel_user_id)
            from_user = UserProfile.objects.get(user=request.user)
            existing_request = FriendRequest.objects.filter(from_user=from_user, to_user=to_user).first()

            # Check if users are already friends
            if from_user.friends.filter(pk=sel_user_id).exists():
                messages.warning(request, f'You are already friends with {to_user.user}.')

            # check if to_user and from_user is same
            elif to_user == from_user:
                messages.warning(request, 'Invalid Move!!.')
            # Check if a friend request already exists
            elif existing_request:
                messages.warning(request, 'Request is already sent.')
            else:
                messages.success(request, 'Request sent.')
                return redirect(f'/send_friend_request/{sel_user_id}/')

        elif request.POST.get('searchForm'):
            inp = request.POST.get('searchForm')
            # for email
            user_with_email = User.objects.filter(email=inp)
            # for username
            user_with_username = User.objects.filter(username__icontains=inp).exclude(username=request.user)
            if user_with_username:
                try:
                    user_u = User.objects.get(username=inp)
                    user_pro = UserProfile.objects.get(user=user_u)
                    user_idd = user_pro.id
                except User.DoesNotExist or UserProfile.DoesNotExist:
                    user_idd = None
                # print(user_pro.user_id,user.id)
            else:
                try:
                    user_u = User.objects.get(email=inp)
                    user_pro = UserProfile.objects.get(user=user_u)
                    user_idd = user_pro.id
                except User.DoesNotExist or UserProfile.DoesNotExist:
                    user_idd = None

            if user_with_email:
                curr_search = user_with_email[0].username
                res = True
            elif user_with_username:
                curr_search = user_with_username[0].username
                res = True
            else:
                curr_search = "User Not Found"

        elif request.POST.get('friends'):
            return redirect('/friends_list')

        elif request.POST.get('sent_request'):
            return redirect('/sent_request')

        elif request.POST.get('new_post'):
            return redirect('/create_post')

    context = {
        'user_profile': user_profile,
        'all_user': users,
        'all_post': totalPost,
        'found': res,
        'search': curr_search,
        'pending': pending_requests_count,
        'friends': friends,
        'sent_request': sent_request,
        'user_id': user_idd,
        'isHome': False,
        'isFriend': res_query,
        'isSent': True,
        'myProfile': "My"
    }

    return render(request, 'displayProfile.html', context)


def get_all_user(request):
    print("users")

    usernames = User.objects.values('username')
    print(usernames)
    return JsonResponse({'usernames': list(usernames)})
    # data = serializers.serialize('json', users)
    # print(data)
    # return JsonResponse({'users': data}, safe=False)
    # return JsonResponse(users,safe=False)

# profile page view
@csrf_exempt
def create_profile(request, username=None):
    # create a check if you are not re entering a record
    if request.method == 'POST':
        user_name = request.POST.get('username')
        dob = request.POST.get('DOB')
        loc = request.POST.get('location')
        image = request.FILES.get('Profile_Image')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        school = request.POST.get('school')
        bio = request.POST.get('bio')
        interest = request.POST.get('interest')
        print(user_name,"sam",dob,loc," ",image, end="\n")
        dateTimeObj = datetime.strptime(dob, "%Y-%m-%d")
        user_obj = User.objects.get(username=user_name)
        print(user_obj)
        # Check if a UserProfile already exists for the user
        try:
            user_profile = UserProfile.objects.get(user=user_obj)
            print("new")
        except UserProfile.DoesNotExist:
            user_profile = UserProfile()
            print("old")

        user_profile.user = user_obj
        user_profile.dob = dateTimeObj
        user_profile.location = loc
        user_profile.profile_image = image
        user_profile.phone = phone
        user_profile.gender = gender
        user_profile.school = school
        user_profile.bio = bio
        user_profile.interest = interest
        user_profile.save()
        # print("save")
        return JsonResponse({'message': 'Profile created successfully!!'})
        # return redirect('display_profile')
    return JsonResponse({'message': 'Invalid request method'})
    # return render(request, 'profile.html', {'username': username})


def get_user_data(request, username=None):
    print("get")
    user_obj = User.objects.get(username=username)
    user_profile = UserProfile.objects.get(user=user_obj)
    user_profile_data = {
        'username': username,
        'loc': user_profile.location,
        'dob': user_profile.dob,
        'image': user_profile.profile_image.url,
        'phone': user_profile.phn_num,
        'gender': user_profile.gender,
        'bio': user_profile.bio,
        'interest': user_profile.interest,
        'school': user_profile.school
    }
    print("get2")
    return JsonResponse(user_profile_data)


# signup page VIEW
@csrf_exempt
def signup(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        r = User.objects.filter(username=uname)
        # check if user already exist
        if r.count():
            return HttpResponse('Username already exists', status=400)
            # return render(request, 'signup.html', {'error': 'username exist'})

        email = request.POST.get('email')
        # check if email already exist
        r = User.objects.filter(email=email)
        if r.count():
            return HttpResponse('Email already exists', status=400)
            # return render(request, 'signup.html', {'error': 'email exist'})

        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if pass1 != pass2:
            return HttpResponse('passwords do not match', status=400)
            # return render(request, 'signup.html', {'error': 'passwords do not match'})
        else:
            my_user = User.objects.create_user(uname, email, pass1)
            my_user.save()
            return JsonResponse({'message': 'user registered successfully'})
            # return redirect('login')
    return render(request, 'signup.html')


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        print('Test!!!')
        username = request.POST.get('username')
        pass1 = request.POST.get('password')
        print(username," ",pass1)
        user = authenticate(request, username=username, password=pass1)
        print("log")
        if user is not None:
            login(request, user)
            curr = User.objects.get(username=username)
            try:
                user_profile = UserProfile.objects.get(user=curr)
            except UserProfile.DoesNotExist:
                user_profile = None

            if not user_profile:
                print("yes")
                return JsonResponse({'message': 'user LoggedIn successfully'}, status=200)
                # return HttpResponse("{'msg': 'User logged in successfully'}", status=200)
                # return HttpResponseRedirect(f'/uploadData/{username}')
            else:
                print("no")
                return JsonResponse({'message': 'user LoggedIn successfully'}, status=200)
                # return HttpResponse("{'msg': 'User logged in successfully'}", status=200)
                # return HttpResponseRedirect('/displayProfile')
        else:
            return JsonResponse({'error': 'invalid request method'}, status=401)
            # return HttpResponse("{'msg': 'Invalid login credentials'}", status=401)
    # return HttpResponse('Invalid request method', status=405)
    # return render(request, 'login.html', {'error': 'Invalid username or password'})



