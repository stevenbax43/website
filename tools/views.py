from django.shortcuts import render 
from .models import adress
from django.http import FileResponse
from .API import BAG_data, EP_API, Weii_API
from .pdf import generate_pdf, google_maps
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone

def tools(request):
    return render(request, 'tools/tools_index.html')

# Create your views here.
@login_required(login_url='accounts:login')
def tool_A1(request):  
    adr1 = adress()
    EPcolor = "black"
    color_mapping = {'A++': 'dark-green', 'A+':'green','A':'light-green', 'B': 'yellow', 'C': 'orange', 'D': 'dark-orange', 'E': 'light-red','F': 'red'}
    if request.method =='POST':
        #print(request.POST)
        #get all input values
        adr1.pcode = request.POST.get('pcode')
        adr1.hnumber = request.POST.get('hnumber')
        adr1.addition = request.POST.get('addition')
        adr1.calendaryear = request.POST.get('calendaryear')
        adr1.elektra = request.POST.get('elektra')
        adr1.gas = request.POST.get('gas')
        
        if adr1.pcode != "" and adr1.hnumber != "":

            if 'BAG_button'   in request.POST:
                adr1 = BAG_data(adr1)
                
            elif 'EP_button' in request.POST:
                adr1 = BAG_data(adr1)
                adr1 = EP_API(adr1)
                EPcolor = color_mapping.get(adr1.EP_label, "black") # default is black

            elif 'WEii_button' in request.POST:
                adr1 = BAG_data(adr1)
                adr1 = EP_API(adr1)
                adr1 = Weii_API(adr1)
                adr1.weii = str(adr1.weii) + ' kWh/m²'
                EPcolor = color_mapping.get(adr1.EP_label, "black") # default is black
            
            elif 'PDF_creater' in request.POST:
                adr1 = BAG_data(adr1)
                adr1 = EP_API(adr1)
                adr1 = Weii_API(adr1)
                adr1.weii = str(adr1.weii) + ' kWh/m²'
                #check als pcode en hnumber al een keer is opgeslagen. 
                existing_record = adress.objects.filter(pcode=adr1.pcode, hnumber=adr1.hnumber).first()
                if existing_record:
                    adr1.date = timezone.now().strftime("%d-%m-%Y %H:%M")
                    for field in adr1._meta.fields:
                        setattr(existing_record, field.name, getattr(adr1, field.name))                      
                        existing_record.save()
                else:
                    adr1.save()
                EPcolor = color_mapping.get(adr1.EP_label, "black") # default is black
                #google_maps(adr1)
                # Generate PDF content using PyPDF2
                pdf_buffer  = generate_pdf(adr1)
                # Create a FileResponse and set the content type and content-disposition
                response = FileResponse(pdf_buffer, content_type='application/pdf')
                response['Content-Disposition'] = 'attachment; filename="'+ adr1.street + ', ' + adr1.hnumber + ', '+ str(adr1.date) + ' ' +'.pdf"'

                return response

    return render(request, 'tools/tool_A1.html', {'adr1': adr1, 'EPcolor': EPcolor})



@login_required(login_url='accounts:login')
def tool_A2_1(request):
    return render(request, 'tools/tool_A2_1.html') #render the html inside the tools file of templates whitin the toolsapp
@login_required(login_url='accounts:login')
def tool_A2_2(request):
    return render(request, 'tools/tool_A2_2.html')
@login_required(login_url='accounts:login')
def tool_A2_3(request):
    return render(request, 'tools/tool_A2_3.html')
@login_required(login_url='accounts:login')
def tool_A2_4(request):
    return render(request, 'tools/tool_A2_4.html')
@login_required(login_url='accounts:login')
def tool_A2_5(request):
    return render(request, 'tools/tool_A2_5.html')

def tool_W1(request):
    return render(request, 'tools/tool_W1.html')