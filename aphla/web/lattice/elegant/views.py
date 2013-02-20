# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django.core.servers.basehttp import FileWrapper
from django import forms
from django.shortcuts import render

from elegant.models import Channel

import StringIO

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)
    choice = forms.ChoiceField(widget=forms.RadioSelect, choices=(
            ('1', 'First'), ('2', 'Second'), ('3', 'Third')))


def index(request):
    latest_ch_list = Channel.objects.filter(pv__startswith='V:2')
    template = loader.get_template('elegant/index.html')
    context = Context({'latest_ch_list': latest_ch_list,})
    return HttpResponse(template.render(context))

def download(request):
    buf = StringIO.StringIO()
    buf.write("test")
    buf.seek(0)
    response = HttpResponse(buf.read(), mimetype='application/lte')
    response['Content-Disposition'] = 'attachment; filename=test.lte'
    #response['Content-Length'] = buf.tell()
    return response

def contact(request):
    if request.method == 'POST':
        return HttpResponseRedirect('/')
    else:
        form = ContactForm()

    return render(request, 'elegant/contact.html', {'form': form})
