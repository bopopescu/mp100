from celery.task import task

@task
def startTemporada():
    from fotos.models import start_temporada as models_start_temporada
    return models_start_temporada()
        
@task
def closeTemporada():
    from fotos.models import close_temporada as models_close_temporada
    return models_close_temporada()

@task
def weeklyTopAmbassadors():
    from fotos.models import weekly_top_ambassadors as models_weekly_top_ten
    return models_weekly_top_ten()






