from django.shortcuts import render
from polls import forms
from polls.models import User, Question, AccessToken, Answer
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from polls.async_email import EmailThread
from django import forms as django_forms
from django.http import HttpResponseRedirect
from django.contrib import messages

def send_email(subject, user, question, token, domain, voting=False): 
    subject = subject
    message = render_to_string('access_question.html', {
        'user': user,
        'domain': domain,
        'uid': user.id,
        'qid': question.id,
        'token': token,
        'voting': voting,
    })
    print(message)
    print(user.email)
    EmailThread(subject, message, 'support@localhost', [user.email], fail_silently=False).start()

def send_result(subject, user, question, domain):
    answers = question.answer_set.all().order_by('-votes')
    total_count = len(answers)
    for answer in answers:
        answer.avg = answer.votes/total_count*100
    message = render_to_string('result.html', {
        'answers': answers,
        'question': question
    })
    EmailThread(subject, message, 'support@localhost', [user.email], fail_silently=False).start()
    user.delete()

def generate_token():
    return get_random_string(length=32)

def new_poll(request):
    formset = forms.UserFormSet(queryset = User.objects.none())
    #formset = forms.UserFormSet()
    
    if request.method == 'POST':
        question_text = request.POST['question']
        question = Question.objects.create(question_text=question_text)
        formset = forms.UserFormSet(request.POST)
        if formset.is_valid(): 
            if formset.has_changed():
                users = formset.save()
                for user in users:
                    token = generate_token()
                    access_token = AccessToken.objects.create(user=user, 
                                                            question=question,
                                                            question_token=token)
                    domain = get_current_site(request)
                    send_email('New Poll!', user, question, token, domain)
                messages.success(request, "Your poll was successfully created and sent to users!")
                return HttpResponseRedirect('/polls/success')
            else:
                raise django_forms.ValidationError("Please enter atleast one user details")      

    return render(request, '../templates/new_poll.html', {
        'user_formset': formset
    })

def collect_answer(request, uid, qid, token):
    question = Question.objects.get(pk=qid)
    if(question.is_active is False):
        messages.error(request, "This poll is no longer active!")
        return HttpResponseRedirect('/polls/error')
    
    user = User.objects.get(pk=uid)
    usertoken = AccessToken.objects.get(question=qid, user=uid)    

    if(usertoken.question_token is None):
        messages.info(request, "Your response has already been submitted!")
        return HttpResponseRedirect('/polls/success')

    if(usertoken.question_token != token):
        messages.error(request, "Sorry! You do not have access to the poll")
        return HttpResponseRedirect('/polls/error')

    if request.method == 'POST':
        # add new answer to poll
        answer_text = request.POST['answer']
        answer = Answer.objects.create(question=question, answer_text=answer_text)
        
        # delete one time access token to view poll
        accesstoken = AccessToken.objects.get(user=uid, question=qid)
        accesstoken.question_token = None
        accesstoken.save()

        # check if all users have sumbitted answers
        submitted = True
        tokens = AccessToken.objects.filter(question=qid)
        for token in tokens:
            if token.question_token != None:
                submitted = False
                break
        if(submitted):
            for token in tokens:
                token.voting_token = generate_token()
                token.save()
                domain = get_current_site(request)
                send_email('Voting Begun!', token.user, token.question, token.voting_token, domain, voting=True)

        messages.success(request, "You will be notified when the poll is open for voting")
        return HttpResponseRedirect('/polls/success')

    return render(request, '../templates/answer_poll.html', {
    'question': question
    })

def collect_vote(request, uid, qid, token):
    question = Question.objects.get(pk=qid)
    if(question.is_active is False):
        messages.error(request, "This poll is no longer active!")
        return HttpResponseRedirect('/polls/error')
    
    answers = Answer.objects.filter(question=qid)
    usertoken = AccessToken.objects.get(question=qid, user=uid)    

    if(usertoken.voting_token is None):
        messages.info(request, "Your response has already been submitted!")
        return HttpResponseRedirect('/polls/success')

    if(usertoken.voting_token != token):
        messages.error(request, "Sorry! You do not have access to the poll")
        return HttpResponseRedirect('/polls/error')

    if request.method == "POST":
        selected_answer = question.answer_set.get(pk=request.POST['answer'])
        selected_answer.votes += 1
        selected_answer.save()

        accesstoken = AccessToken.objects.get(user=uid, question=qid)
        accesstoken.voting_token = None
        accesstoken.save()

        submitted = True
        tokens = AccessToken.objects.filter(question=qid)
        for token in tokens:
            if token.voting_token != None:
                submitted = False
                break
        if(submitted):
            question.is_active = False
            question.save()
            domain = get_current_site(request)
            for token in tokens:
                send_result('Poll Results are Out!', token.user, token.question, domain)

        messages.success(request, "You will be notified when the poll results are out")
        return HttpResponseRedirect('/polls/success')
    return render(request, '../templates/vote_poll.html', {
    'question': question,
    'answers': answers
    })