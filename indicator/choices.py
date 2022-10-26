from django.utils.translation import gettext as _


languages = (
    ('', ''),
    ('Pt', 'Pt'),
    ('Es', 'Es'),
    ('En', 'En'),
)


WIP = 'WIP'
TO_MODERATE = 'TO MODERATE'
PUBLISHED = 'PUBLISHED'

status = (
    ('', ''),
    (WIP, _('WORK IN PROGRESS')),
    (TO_MODERATE, _('TO MODERATE')),
    (PUBLISHED, _('PUBLISHED')),
)

CURRENT = 'CURRENT'
OUTDATED = 'OUTDATED'

VALIDITY = (
    ('', ''),
    (CURRENT, _('CURRENT')),
    (OUTDATED, _('OUTDATED')),
)

open_access = (
    ('', ''),
    ('NOT', _('NOT')),
    ('YES', _('YES')),
    ('ALL', _('ALL')),
    ('NOT APPLICABLE', _('NOT APPLICABLE')),
    ('UNDEFINED', _('UNDEFINED')),
)

classification = (
    ('', ''),
    ('curso livre', _('curso livre')),
    ('disciplina de graduação', _('disciplina de graduação')),
    ('disciplina de lato sensu', _('disciplina de lato sensu')),
    ('disciplina de stricto sensu', _('disciplina de stricto sensu')),
    ('encontro', _('encontro')),
    ('conferência', _('conferência')),
    ('congresso', _('congresso')),
    ('workshop', _('workshop')),
    ('seminário', _('seminário')),
    ('outros', _('outros')),
    ('portal', _('Portal')),
    ('plataforma', _('Plataforma')),
    ('servidor', _('Servidor')),
    ('repositório', _('Repositório')),
    ('serviço', _('Serviço')),
    ('promoção', _('promoção')),
    ('posicionamento', _('posicionamento')),
    ('mandato', _('mandato')),
    ('geral', _('geral')),
    ('outras', _('Outras')),
)


INSTITUTIONAL = 'INSTITUTIONAL'
THEMATIC = 'THEMATIC'
GEOGRAPHIC = 'GEOGRAPHIC'
CHRONOLOGICAL = 'CHRONOLOGICAL'

SCOPE = (
    ('', ''),
    (INSTITUTIONAL, _('Instituticional')),
    (GEOGRAPHIC, _('Geográfico')),
    (CHRONOLOGICAL, _('Cronológico')),
    (THEMATIC, _('Temático')),
)

FREQUENCY = 'FREQUENCY'
PERCENTUAL = 'PERCENTUAL'
EVOLUTION = 'EVOLUTION'
AVERAGE = 'AVERAGE'

MEASUREMENT_TYPE = (
    ('', ''),
    (FREQUENCY, _('Frequência')),
    (EVOLUTION, _('Evolução')),
    (AVERAGE, _('Média')),
    (PERCENTUAL, _('Percentual')),
)
