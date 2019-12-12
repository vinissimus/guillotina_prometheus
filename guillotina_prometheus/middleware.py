from guillotina.utils import get_dotted_name
from guillotina_prometheus import metrics
from guillotina.interfaces import IApplication
from guillotina.interfaces import IDatabase
from guillotina.component import get_utility


class Handler:

    def __init__(self, app, handler):
        self.app = app
        self.handler = handler
        self.root = get_utility(IApplication, name="root")

    async def __call__(self, request):
        try:
            try:
                view_name = get_dotted_name(request.found_view.view_func)
            except AttributeError:
                view_name = get_dotted_name(request.found_view)
        except AttributeError:
            view_name = 'unknown'

        for _, db in self.root:
            if IDatabase.providedBy(db):
                pool = db.storage.pool
                metrics.g_pg_conn_total.labels(db=db.id).set(len(pool._holders))
                metrics.g_pg_conn_avail.labels(db=db.id).set(pool._queue.qsize())

        resp = await self.handler(request)

        metric = metrics.request_summary.labels(
            method=request.method,
            view=view_name,
            response_code=resp.status)

        try:
            metric.observe(request.events['finish'] - request.events['start'])
        except (AttributeError, KeyError):
            pass

        return resp


async def middleware_factory(app, handler):
    return Handler(app, handler)
