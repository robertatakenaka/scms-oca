from django.utils.translation import gettext as _


TYPE_OF_RESOURCE = [
    ('', _('NOT APPLICABLE')),
    ("book", _("Book")),
    ("book-chapter", _("Book Chapter")),
    ("book-part", _("Part")),
    ("book-section", _("Book Section")),
    ("book-series", _("Book Series")),
    ("book-set", _("Book Set")),
    ("book-track", _("Book Track")),
    ("component", _("Component")),
    ("database", _("Database")),
    ("dataset", _("Dataset")),
    ("dissertation", _("Dissertation")),
    ("edited-book", _("Edited Book")),
    ("grant", _("Grant")),
    ("journal", _("Journal")),
    ("journal-article", _("Journal Article")),
    ("journal-issue", _("Journal Issue")),
    ("journal-volume", _("Journal Volume")),
    ("monograph", _("Monograph")),
    ("other", _("Other")),
    ("peer-review", _("Peer Review")),
    ("posted-content", _("Posted Content")),
    ("proceedings", _("Proceedings")),
    ("proceedings-article", _("Proceedings Article")),
    ("proceedings-series", _("Proceedings Series")),
    ("reference-book", _("Reference Book")),
    ("reference-entry", _("Reference Entry")),
    ("report", _("Report")),
    ("report-component", _("Report Component")),
    ("report-series", _("Report Series")),
    ("standard", _("Standard")),
    ("standard-series", _("Standard Series")),
]

OA_STATUS = [
    ("", ""),
    ("gold", _("Gold")),
    ("hybrid", _("Hybrid")),
    ("bronze", _("Bronze")),
    ("green", _("Green")),
    ("closed", _("Closed")),
]

LICENSE = [
    ("", ""),
    ("CC0", "CC0"),
    ("CC-BY", "CC-BY"),
    ("CC-BYNC", "CC-BYNC"),
    ("CC-BYND", "CC-BYND"),
    ("CC-BYNCND", "CC-BYNCND"),
]

APC = [
    ("", ""),
    ("YES", "YES"),
    ("NO", "NO"),
]

SOURCE = [
    ("", ""),
    ("UNPAYWALL", "UNPAYWALL"),
]
