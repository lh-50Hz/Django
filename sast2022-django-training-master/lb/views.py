from re import S
from xmlrpc.client import ProtocolError
from django.http import (
    HttpRequest,
    JsonResponse,
    HttpResponseNotAllowed,
)
from .models import Submission, User
from django.forms.models import model_to_dict
from django.db.models import F
import json
from . import utils
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.views.decorators.http import require_http_methods as method

def hello(req: HttpRequest):
    return JsonResponse({
        "code": 0,
        "msg": "hello"
    })

@method(['GET'])
def leaderboard(req: HttpRequest):
    return JsonResponse(
        utils.get_leaderboard(),
        safe=False,
    )


@method(["GET"])
def history(req: HttpRequest, username: str):
    # TODO: Complete `/history/<slug:username>` API
    list = utils.get_leaderboard()
    flag = False
    fin_list = []
    subkey = ['score', 'subs', 'time']
    for dict in list:
        if(dict['user'] == username):
            flag = True
            fin_list += [{k:v for k,v in dict.items() if k in subkey}]
    if(not flag):
        return JsonResponse(
            {
                "code": -1 
            },
        )
    return JsonResponse(
        fin_list,
        safe=False,
    )
    

@method(["POST"])
@csrf_exempt
def submit(req: HttpRequest):
    # TODO: Complete `/submit` API
    post_dict = json.loads(req.body)
    if(
        post_dict.get('user', 'homo') == 'homo' or
        post_dict.get('avatar', 'homo') == 'homo' or
        post_dict.get('content', 'homo') == 'homo'
    ):
        return JsonResponse({ 
            "code": 1,
            "msg": "参数不全啊",
        })
    if(len(post_dict['user']) > 255):
        return JsonResponse({ 
            "code": -1,
            "msg": "用户名太长了",
        })
    if(len(post_dict['avatar']) > 100_000):
        return JsonResponse({
            "code": -2,
            "msg": "图像太大了",
        })
    subs1=[0, 0, 0]
    total, subs1[0], subs1[1], subs1[2] = utils.judge(post_dict['content'])
    if(total == 1919810):
        return JsonResponse({
            "code": -3,
            "msg": "提交内容非法呜呜"
        })
    try:
        US = User.objects.get(username = post_dict['user'])
    except(Exception):
        User.objects.create(username = post_dict['user'], id = User.objects.all().count() + 1)
        US = User.objects.get(username = post_dict['user'])
    Submission.objects.create(id = Submission.objects.all().count() + 1, user = US, avatar = post_dict['avatar'], score = total, subs = str(subs1[0])+' '+str(subs1[1])+' '+str(subs1[2]))
    return JsonResponse({
        "code": 0,
        "msg": "提交成功",
        "data": { "leaderboard": utils.get_leaderboard() }
    })
@method(["POST"])
@csrf_exempt
def vote(req: HttpRequest):
    if 'User-Agent' not in req.headers or 'requests' in req.headers['User-Agent']:
        return JsonResponse({
            "code": -1
        })

    # TODO: Complete `/vote` API

    vote_dict = json.loads(req.body)
    try:
        US = User.objects.get(username = vote_dict['user'])
    except(Exception):
        return JsonResponse({
            "code": -1
        })
    goal = User.objects.get(username = vote_dict['user'])
    goal.votes = F('votes') +1
    goal.save()
    return JsonResponse({
        "code": 0,
        "data": {
            "leaderboard": utils.get_leaderboard()
        }
    })