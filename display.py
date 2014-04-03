import HotDjango
import Imex.models as m
import HotDjango

app_name='imex'


class Process(HotDjango.ModelDisplay):
    display = False
    
    class HotTable(HotDjango.ModelSerialiser):
        class Meta:
            fields = ('id', 'log', 'errors', 'complete', 'successful', 'imex_file')