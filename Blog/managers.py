from django.db.models import Manager


class PostManager(Manager):
    def get_published(self, order='-date_published', *args, **kwargs):
        """
        Returns
            QuerySet
                the set of posts that are published
        Args
            order: str
                The field according to which the list will be sorted
        """
        return self.filter(state=self.model.Status.PUBLISH, *args, **kwargs).order_by(order)

    def get_queued(self, order='-date_created', *args, **kwargs):
        """
        Returns
            QuerySet
                the set of posts that are published
        Args
            order: str
                The field according to which the list will be sorted
        """
        return self.filter(state=self.model.Status.QUEUE, *args, **kwargs).order_by(order)

    def get_draft(self, order='-date_created', *args, **kwargs):
        return self.filter(state=self.model.Status.DRAFT, *args, **kwargs).order_by(order)

    def latest_entry(self):
        """
        Returns
            date: date-time
                The date of the latest post published.
        """
        return self.get_published().first().date_published
