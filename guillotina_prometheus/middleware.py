from guillotina.utils import get_dotted_name
from guillotina import task_vars
from guillotina_prometheus import metrics
from guillotina.interfaces import IApplication
from guillotina.interfaces import IDatabase
from guillotina.component import get_utility


class PrometheusMiddleware:

    def __init__(self, app):
        self.next_app = app
        self.root = get_utility(IApplication, name="root")

    async def __call__(self, scope, receive, send):
        for _, db in self.root:
            if IDatabase.providedBy(db):
                pool = db.storage.pool
                metrics.g_pg_conn_total.labels(db=db.id).set(len(pool._holders))
                metrics.g_pg_conn_avail.labels(db=db.id).set(pool._queue.qsize())

        resp = None
        try:
            resp = await self.next_app(scope, receive, send)
        finally:
            request = task_vars.request.get()
            try:
                try:
                    view_name = get_dotted_name(request.found_view.view_func)
                except AttributeError:
                    view_name = get_dotted_name(request.found_view)
            except AttributeError:
                view_name = 'unknown'

            metric = metrics.request_summary.labels(
                method=request.method,
                view=view_name,
                response_code=resp.status if resp else 500)

            try:
                metric.observe(request.events['finish'] - request.events['start'])
            except (AttributeError, KeyError):
                pass
        return resp
