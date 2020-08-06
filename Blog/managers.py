from django.db.models import Manager


class PostManager(Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_published(self, order='-date_published'):
        """
        Returns
            QuerySet
                the set of posts that are published
        Args
            order: str
                The field according to which the list will be sorted
        """
        return self.filter(state=self.model.Status.PUBLISH).order_by(order)

    def get_queued(self, order='-date_created'):
        """
        Returns
            QuerySet
                the set of posts that are published
        Args
            order: str
                The field according to which the list will be sorted
        """
        return self.filter(state=self.model.Status.QUEUE).order_by(order)

    def get_draft(self, order='-date_created'):
        return self.filter(state=self.model.Status.DRAFT).order_by(order)

    def latest_entry(self):
        """
        Returns
            date: date-time
                The date of the latest post published.
        """
        return self.get_published().first().date_published
