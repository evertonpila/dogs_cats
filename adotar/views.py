from django.shortcuts import render
from divulgar.models import Pet, Raca,Animal
from django.shortcuts import redirect
from django.contrib.messages import constants
from django.contrib import messages
from .models import PedidoAdocao
from  datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.core.paginator import Paginator

@login_required


def listar_pets(request):
    pets = Pet.objects.filter(status='P')
    racas = Raca.objects.all()
    animals = Animal.objects.all()

    cidade = request.GET.get('cidade')
    raca_filter = request.GET.get('raca')
    animal_filter = request.GET.get('animal')

    if cidade:
        pets = pets.filter(cidade__icontains=cidade)

    if raca_filter:
        pets = pets.filter(raca__id=raca_filter)
        raca_filter = Raca.objects.get(id=raca_filter)

    if animal_filter:
        pets = pets.filter(animal__id=animal_filter)
        animal_filter = Animal.objects.get(id=animal_filter)

    paginator = Paginator(pets,6)
    page = request.GET.get('page')
    pets_list = paginator.get_page(page)



    return render(request, 'listar_pets.html', {'pets': pets,'animals':animals, 'racas': racas, 'cidade': cidade, 'raca_filter': raca_filter,'animal_filter':animal_filter, 'pets_list': pets_list})


@login_required
def pedido_adocao(request, id_pet):
    pet = Pet.objects.filter(id=id_pet).filter(status="P")
    if not pet.exists():
        messages.add_message(request, constants.WARNING,'Esse pet já foi adotado ')
        return redirect('/adotar')
       
    pedido = PedidoAdocao(pet=pet.first(),
                         usuario=request.user,
                          data=datetime.now())

    pedido.save()

    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção realizado, você receberá um e-mail caso ele seja aprovado.')
   
    
    return redirect('/adotar')
    
@login_required
def processa_pedido_adocao(request, id_pedido):
    status = request.GET.get('status')
    pedido = PedidoAdocao.objects.get(id=id_pedido)
    if status == "A":
        pedido.status = 'AP'
        string = '''Olá, sua adoção foi aprovada. ...'''
    elif status == "R":
        string = '''Olá, sua adoção foi recusada. ...'''
        pedido.status = 'R'

    pedido.save()

  
    #todo: alterar o

    print(pedido.usuario.email)
    email = send_mail(
        'Sua adoção foi processada',
        string,
        'caio@pythonando.com.br',
        [pedido.usuario.email,],
    )
    
    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção processado com sucesso')
    return redirect('/divulgar/ver_pedido_adocao')




