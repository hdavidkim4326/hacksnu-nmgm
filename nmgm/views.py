from django.shortcuts import render

# 랜딩 페이지만을 보여주는 뷰 함수입니다.
def landing_view(request):
    return render(request, 'nmgm/landing.html')