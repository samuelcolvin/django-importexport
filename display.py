import SkeletalDisplay
import Imex.models as m
import HotDjango

app_name='imex'


class Process(SkeletalDisplay.ModelDisplay):
    model = m.Process
    display = False
    
    class HotTable(HotDjango.ModelSerialiser):
        class Meta:
            fields = ('id', 'log', 'errors', 'complete', 'successful', 'imex_file')