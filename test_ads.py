import time
from ads import electric_record_from_ads, get_ads_interface

ads = get_ads_interface()

while True:
    if ads is not None:
        electric_record_from_ads(ads)
    time.sleep(0.5)
