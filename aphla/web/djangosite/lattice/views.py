# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, loader
from django.core.servers.basehttp import FileWrapper
from django import forms
from django.shortcuts import render

from lattice.models import Channel

import StringIO, tempfile, os, commands

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()
    cc_myself = forms.BooleanField(required=False)
    choice = forms.ChoiceField(widget=forms.RadioSelect, choices=(
            ('1', 'First'), ('2', 'Second'), ('3', 'Third')))

class LatticeForm(forms.Form):
    fmtchoice = forms.ChoiceField(widget=forms.RadioSelect, choices=(
            ('EL', 'Elegant'), ('TR', 'Tracy (Not Available yet)'),
            ('MAD', 'MAD ? NO'), ('AT', 'AT ? check Matlab Middle Layer')))
    

def index(request):
    #latest_ch_list = Channel.objects.using("lattice").filter(pv__startswith='V:2')
    #template = loader.get_template('lattice/index.html')
    #context = Context({'latest_ch_list': latest_ch_list,})
    #return HttpResponse(template.render(context))

    if request.method == 'POST':
        form = LatticeForm(request.POST)
        if form.is_valid():
            fmtchoice = form.cleaned_data['fmtchoice']
            if fmtchoice == 'EL':
                return HttpResponseRedirect('/lattice/elegant')
            else:
                return HttpResponse("Unknown response")
    else:
        form = LatticeForm()

    return render(request, 'lattice/index.html', {'form': form})

def download(request):
    buf = StringIO.StringIO()
    eledir = request.session.get('eledir', None)
    eleroot = request.session.get('eleroot', None)
    lte = os.path.join(eledir, eleroot + ".lte")
    if os.path.exists(lte):
        buf.write(open(lte, 'r').read())
    buf.seek(0)
    response = HttpResponse(buf.read(), mimetype='application/lte')
    response['Content-Disposition'] = 'attachment; filename=nsls2.lte'
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
    # this is a hack for NSLS2, rect dipole
    mp = {'BPM': 'MONI', 'TRIMX': 'HKICK', 'TRIMY': 'VKICK', 
          'FTRIM': 'KICK', 'SQ_TRIM': 'KICK', 'TRIMD': 'KICK',
          'DIPOLE': 'SBEN' }
    for s in open('lattice/ring_par.txt', 'r').readlines()[3:]:
        name, tp, L, se, k1, k2, angle, km = (s.split() + [None, None])[:8]
        if name == '_BEG_': continue
        if tp in mp:
            rec = "%s: %s" % (name, mp[tp])
        else:
            rec = "%s: %s" % (name, tp)

        if tp in ['MARK', 'BPM']:
            pass
        elif tp in ['FTRIM', 'SQ_TRIM', 'TRIMD', 'TRIMX', 'TRIMY']:
            rec += ", L={0}".format(L)
        elif tp == 'DRIF':
            rec += ", L={0}".format(L)
        elif tp == 'DIPOLE':
            rec += ", L={0}, angle={1}, E1={2}, E2={3}".format(
                L, angle, float(angle)/2.0, float(angle)/2.0)
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

    # write 
    eledir, eleroot = tempfile.gettempdir(), tempfile.gettempprefix()
    ele = os.path.join(eledir, eleroot + ".ele")
    tmplate = open("lattice/elegant.ele.template", 'r').read()
    f = open(ele, 'w')
    f.write(tmplate % {'lte': eleroot + ".lte"})
    f.close()

    f = open(os.path.join(eledir, eleroot+".lte"), 'w')
    for elem in elemdeflst:
        f.write(elem + "\n")
    f.write("RING: LINE=( %s )" % (",".join(elemlst)))
    f.close()


    cwd = os.getcwd()
    os.chdir(eledir)
    stat, out = commands.getstatusoutput("elegant %s.ele" % eleroot)
    #response = HttpResponse(out.replace('\n', '<br>'))
    #return response
    
    stat, twiss = commands.getstatusoutput("sddsprintout -col={ElementName,s,betax,betay,etax,psix,psiy} %s.twi" % eleroot)

    #buf.seek(0)
    #response = HttpResponse(buf.read(), mimetype='application/lte')
    #response['Content-Disposition'] = 'attachment; filename=test.lte'
    ##response['Content-Length'] = buf.tell()
    #return response

    os.chdir(cwd)

    request.session['eledir']  = eledir
    request.session['eleroot'] = eleroot

    template = loader.get_template('lattice/elegant.html')
    val = {'ele': open(ele, 'r').read(), 
                       'lte': open(os.path.join(
                    eledir, eleroot+".lte"), 'r').read(),
                       'stdout' : out,
                       'twiss' : twiss,}
    #return HttpResponse(template.render(context))
    return render(request, 'lattice/elegant.html', val)
