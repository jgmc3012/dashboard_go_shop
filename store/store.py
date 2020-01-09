from meli_sdk.sdk.meli import Meli
from decouple import config


class Store(Meli):
    def __init__(self):
        self.app_id = config('MELI_APP_ID')
        self.client_secret = config('MELI_SECRET_KEY')
        super().__init__(self.app_id, self.client_secret)
        self.publications = []
        self.SELLER_ID = 503380447
        self.pools = []



    def get_items_for_seller(self):
    global executor, results, event
    path = f"/users/{self.SELLER_ID}/items/search"
    limit_per_request = 100
    params = {
        'access_token': self.access_token,
        'limit': limit_per_request,
        'search_type': 'scan',
    }

    data = self.get(path, params) #Este Actualmente retorna un elemento response normal
    data_push_ids(data)
    total = data.get('paging').get('total')
    params['scroll_id'] = data.get('scroll_id')
    total_of_requests = math.ceil(total/limit_per_request) - 1 #Menos 1 porque ya se realizo una peticion
    
    for i in range(total_of_requests):
        data = request_meli(path,params)
        data_push_ids(data) 
    
    return results

    def data_push_ids(self, data):
        global results, event
        items_ids = data.get('results')
        push_items(items_ids)
        total= data.get('paging').get('total')
        logging.info(f'({len(results)}/{total})')
