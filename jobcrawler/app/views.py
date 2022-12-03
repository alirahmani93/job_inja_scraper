from django.http import HttpResponse

from django.shortcuts import redirect


# Create your views here.
def get_data(request):
    if not request.user.is_superuser:
        return HttpResponse("You are spammer")

    from .scraper import job_inja
    search = request.GET.get('search')
    # job_inja.send_first_request(title='python')
    redirect_to = request.GET.get('next', '')
    if redirect_to:
        return redirect(redirect_to)
    else:
        return HttpResponse("OK")
