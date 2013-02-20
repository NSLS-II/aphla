# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader
from django.core.servers.basehttp import FileWrapper
from django import forms
from django.shortcuts import render

from lattice.models import Channel

import StringIO

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)
    choice = forms.ChoiceField(widget=forms.RadioSelect, choices=(
            ('1', 'First'), ('2', 'Second'), ('3', 'Third')))

def index(request):
    latest_ch_list = Channel.objects.using("lattice").filter(pv__startswith='V:2')
    template = loader.get_template('lattice/index.html')
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

    return render(request, 'lattice/contact.html', {'form': form})

def elegant(request):
    elemdeflst, elemidx, elemlst = [], {}, []
    for s in open('lattice/ring_par.txt', 'r').readlines()[3:]:
        name, tp, L, se, k1, k2, angle, km = (s.split() + [None, None])[:8]
        if name == '_BEG_': continue
        rec = "%s: %s" % (name, tp)
        if tp in ['MARK', 'BPM']:
            pass
        elif tp in ['FTRIM', 'SQ_TRIM', 'TRIMD']:
            rec = "{0}: KICK".format(name) 
        elif tp == 'TRIMX':
            rec = "{0}: HKICK".format(name) 
        elif tp == 'TRIMY':
            rec = "{0}: VKICK".format(name) 
        elif tp == 'DRIF':
            rec += ", L={0}".format(L)
        elif tp == 'DIPOLE':
            rec += ", L={0}, angle={1}".format(L, angle)
        elif tp == 'QUAD':
            rec += ", L={0}, K1={1}".format(L, k1)
        elif tp == 'SEXT':
            rec += ", L={0}, K2={1}".format(L, k2)
        elif tp in ['IVU', 'DW', 'EPU']:
            rec = "{0}: DRIFT, L={1}".format(name, L)
        else:
            raise ValueError("unknow type {0} for '{1}'".format(tp, name))

        if name not in elemidx:
            elemdeflst.append(rec)
            elemidx.setdefault(name, len(elemdeflst)-1)
        elif rec != elemdeflst[elemidx[name]]:
            raise RuntimeError("{0} was defined as {1}, different from this new definition '{2}'".format(name, elemdeflst[elemidx[name]], rec))

        elemlst.append(name)

    template = loader.get_template('lattice/lattice.html')
    context = Context({'element_deflist': elemdeflst, 'element_list': elemlst,})
    return HttpResponse(template.render(context))
