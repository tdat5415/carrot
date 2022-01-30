from django import forms
from function.crypto import get_random_str
from django import forms

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()

# 파일 저장
def upload_file(request, name):
    data = {}
    form = UploadFileForm(request.POST, request.FILES)
    # form = UploadFileForm(request.FILES)
    if not form.is_valid():
        data['state'] = False
        data['detail'] = '파일형식이 맞지않음'
        return True, data

    f = request.FILES['file']
    with open('static/{}'.format(name), 'wb+') as dst:
        for chunk in f.chunks():
            dst.write(chunk)
    return False, None