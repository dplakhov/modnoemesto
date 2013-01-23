class BillingRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'billing' or model._meta.object_name == 'UserOrder':
            return 'billing'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'billing' or model._meta.object_name == 'UserOrder':
            return 'billing'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'billing' and obj2._meta.app_label == 'billing':
            return True
        return None

    def allow_syncdb(self, db, model):
        is_userorder = model._meta.app_label == 'billing' and model._meta.object_name == 'UserOrder'
        if db == 'billing':
            return model._meta.app_label == 'billing' or is_userorder
        elif model._meta.app_label == 'billing' or is_userorder:
            return False
        return None