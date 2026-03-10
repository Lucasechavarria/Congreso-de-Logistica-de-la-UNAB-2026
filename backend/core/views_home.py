from django.http import HttpResponse


from django.http import HttpResponse

def home(request):

    html = """
<h1>Bienvenido a Congreso UNAB API</h1>
<ul>
    <li><a href='/admin/'>/admin/</a> (Panel de administración)</li>
    <li><a href='/api/'>/api/</a> (Root de la API DRF)</li>
    <li><a href='/api/disertantes/'>/api/disertantes/</a></li>
    <li><a href='/api/inscripcion/'>/api/inscripcion/</a></li>
    <li><a href='/api/programa/'>/api/programa/</a></li>
    <li><a href='/api/checkin/'>/api/checkin/</a></li>
</ul>
<p>Documentación y pruebas rápidas de los endpoints principales.</p>
"""
    return HttpResponse(html)
