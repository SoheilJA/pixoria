from django.shortcuts import render


# Create your views here.
def home(request):
    if request.headers.get("HX-Request"):
        return render(request, 'partials/home_content.html')
    return render(request, "pages/home.html")


def about(request):
    if request.headers.get("HX-Request"):
        return render(request, "partials/about_content.html")
    return render(request, "pages/about.html")


def contact(request):
    if request.headers.get('HX-Request'):
        return render(request, 'partials/contact_content.html')
    return render(request, "pages/contact.html")


def services(request):
    if request.headers.get("HX-Request"):
        return render(request, 'partials/services_content.html')
    return render(request, "pages/services.html")
