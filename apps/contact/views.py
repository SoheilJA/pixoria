from django.shortcuts import render
from django.http import HttpResponse
from .models import (
    ContactPageSection,
    ContactInfo,
    ProjectTypeChoice,
    BudgetChoice,
    StartTimeChoice,
    ContactSubmission,
)


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        company = request.POST.get("company", "").strip()
        project_type = request.POST.get("project_type", "").strip()
        budget = request.POST.get("budget", "").strip()
        start_time = request.POST.get("start_time", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not phone or not project_type or not budget or not start_time:
            return HttpResponse(
                '<p style="color: #e74c3c; font-family: var(--mono); font-size: 0.85rem;">لطفاً همه فیلدهای اجباری را پر کنید.</p>'
            )

        ContactSubmission.objects.create(
            name=name,
            phone=phone,
            company=company,
            project_type=project_type,
            budget=budget,
            start_time=start_time,
            message=message,
        )

        return HttpResponse("""
            <div style="
                background: #1a2e1a;
                border: 1px solid #2d5a2d;
                border-radius: 8px;
                padding: 20px 24px;
                display: flex;
                align-items: center;
                gap: 12px;
            ">
                <span style="color: var(--lime); font-size: 1.4rem;">✓</span>
                <div>
                    <p style="color: var(--lime); font-family: var(--mono); font-size: 0.8rem; letter-spacing: 0.1em; text-transform: uppercase; margin: 0 0 4px;">درخواست ارسال شد</p>
                    <p style="color: #c8c7c2; font-size: 0.95rem; margin: 0;">درخواست شما دریافت شد و به زودی با شما تماس می گیریم.</p>
                </div>
            </div>
        """)

    context = {
        "page_section": ContactPageSection.objects.first(),
        "contact_info": ContactInfo.objects.first(),
        "project_types": ProjectTypeChoice.objects.all(),
        "budgets": BudgetChoice.objects.all(),
        "start_times": StartTimeChoice.objects.all(),
    }
    return render(request, "contact/contact.html", context)
