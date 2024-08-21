from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from . import forms
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth import login,logout,authenticate
from . import models
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q

# Create your views here.
@login_required(login_url="/login")
def home(request):
    user = request.user
    problems1 = models.Problem.objects.all().filter(status='P').filter(assign_to=user)
    problems2 = models.Problem.objects.all().filter(status='I').filter(assign_to=user)
    return render(request,'main/home.html',{"list1":problems1,"list2":problems2})

@login_required(login_url="/login")
def all_problems(request):
    query = request.GET.get('q')
    if query:
        filt = models.Problem.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(created_by__username__icontains=query) |
            Q(assign_to__username__icontains=query) |
            Q(status__icontains=query) |
            Q(remark__icontains=query)
        ).order_by('-created_at')
    else:
        filt = models.Problem.objects.all().order_by('-created_at')
    return render(request, 'main/all.html', {"list": filt, "query": query})

@login_required(login_url="/login")
def create_problem(request):
    if request.method == 'POST':
        form= forms.IssueForm(request.POST)
        if form.is_valid:
            post= form.save(commit=False)
            post.created_by= request.user
            post.save()
            return redirect('/home')
    else:
        form=forms.IssueForm()
    
    return render(request,'main/create_post.html', {"form":form})

@login_required
def update_problem(request, pk):
    problem = get_object_or_404(models.Problem, pk=pk)
    previous_description = problem.description
    previous_status = problem.status
    previous_assign = problem.assign_to
    b1 = False
    b2 = False
    b3 = False
    if request.method == 'POST':
        form = forms.PostForm(request.POST, instance=problem)
        if form.is_valid():
            new_description = form.cleaned_data['new_description']
            if new_description.strip():
                problem.description = previous_description + '\n' + '\n'+ new_description
            if form.cleaned_data['assign_to'] != previous_assign:
                problem.assign_to = form.cleaned_data['assign_to']
                b2 = True
            if form.cleaned_data['status'] != previous_status:
                problem.status = form.cleaned_data['status']
                b3 = True
            if new_description.strip():
                b1 = True
            problem.save()
            
            if b1 or b2 or b3:
                models.ProblemUpdate.objects.create(
                    problem=problem,
                    updated_by=request.user,
                    update_description=new_description if b1 else "",
                    update_assign=problem.assign_to if b2 else None,
                    update_status=problem.status if b3 else "",
                    check_assign=b2,
                    check_status=b3,
                    check_description=b1
                )
            return redirect('view_problem', pk=problem.pk)
    else:
        form = forms.PostForm(instance=problem)
    return render(request, 'main/update_post.html', {'form': form, 'problem': problem})


def sign_up(request):
    if request.method == 'POST':
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('login')  # Redirect to login page after successful signup
        else:
            print(form.errors)  # Print form errors to debug
    else:
        form = forms.RegistrationForm()
    return render(request, 'registration/sign-up.html', {"form":form})

def user_page(request, id):
    user = get_object_or_404(User, id=id)
    problems_solved_last_24_hours = models.Problem.objects.filter(assign_to=user, status='C', updated_at__gte=timezone.now()-timedelta(days=1)).count()
    problems_solved_last_month = models.Problem.objects.filter(assign_to=user, status='C', updated_at__gte=timezone.now()-timedelta(days=30)).count()
    total_problems_solved = models.Problem.objects.filter(assign_to=user, status='C').count()
    notifications = models.Notification.objects.filter(recipient=user, read=False)
    
    return render(request, 'main/user_page.html', {
        "user": user,
        "problems_solved_last_24_hours": problems_solved_last_24_hours,
        "problems_solved_last_month": problems_solved_last_month,
        "total_problems_solved": total_problems_solved,
        "notifications": notifications
    })

@login_required
def notifications(request):
    user_notifications = models.Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'main/notifications.html', {'notifications': user_notifications})

@login_required
def mark_notification_as_read(request, id):
    notification = get_object_or_404(models.Notification, id=id)
    notification.read = True
    notification.save()
    return redirect('user_page', id=request.user.id)

def view_problem(request,pk):
    problem = get_object_or_404(models.Problem, pk=pk)
    updates = problem.updates.all().order_by('-updated_at')  # Get all updates for the problem, ordered by update time
    return render(request, 'main/view_problem.html', {'problem': problem, 'updates': updates})