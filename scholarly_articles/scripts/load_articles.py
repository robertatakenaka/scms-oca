from scholarly_articles.tasks import load_journal_articles


def run():
    """
    Load the article to ScholarlyArticles.
    """
    load_journal_articles.apply_async(
        kwargs={
        "user_id": 1,
        "from_year": 1900,
        "resource_type": "journal-article"})
