from django.http import HttpResponse

from .scraper import job_inja
from django.shortcuts import redirect


# Create your views here.
def get_data(request):
    if not request.user.is_superuser:
        return HttpResponse("You are spammer")

    print("AAAAAAAAAAAAAA")
    job_inja.send_first_request(title='python')
    redirect_to = request.GET.get('next', '')
    if redirect_to:
        return redirect(redirect_to)
    else:
        return HttpResponse("OK")


def get_detail_data(request):
    if not request.user.is_superuser:
        return HttpResponse("You are spammer")

    print("BBBBBBBBBB")
    job_inja.get_detail_page()
    redirect_to = request.GET.get('next', '')
    if redirect_to:
        return redirect(redirect_to)
    else:
        return HttpResponse("OK")
