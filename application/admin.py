from flask import redirect, url_for
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_security import current_user
from flask_security.utils import hash_password


class DashboardView(AdminIndexView):
    def is_visible(self):
        return False
    @expose('/')
    def index(self):
        return redirect('/admin/transactions/')

class UsersView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and current_user.is_authenticated)

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('mainpage'))

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = hash_password(model.password)
        else:
            # If provided password is not hash, then make hash
            if len(model.password) != 60:
                model.password = hash_password(model.password)

class RolesView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and current_user.is_authenticated)

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('mainpage'))


class TransactionsView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and current_user.is_authenticated)

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('mainpage'))

    column_default_sort = ('date_of_spent', True)
    column_searchable_list = ('id', 'user_id', 'category_id', 'date_of_spent', 'sum', 'comment')
    #column_labels = dict(id='ID', loanId='Займ', guid='GUID', guidEmployee='GUID сотрудника', phone='Телефон', numOfCards='Кол-во карт', createTime='Время создания (UTC)', address='Адрес страницы', opened='Время открытия (UTC)', dataCollected='Собранные данные', dataReturned='Время передачи в kafka (UTC)')
    column_list = ('id', 'user_id', 'category_id', 'date_of_spent', 'sum', 'comment')

class CategoriesView(ModelView):
    def is_accessible(self):
        return (current_user.is_active and current_user.is_authenticated)

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for('mainpage'))

    column_searchable_list = ('id', 'user_id', 'name', 'comment')
    #column_labels = dict(id='ID', loanId='Займ', guid='GUID', guidEmployee='GUID сотрудника', phone='Телефон', numOfCards='Кол-во карт', createTime='Время создания (UTC)', address='Адрес страницы', opened='Время открытия (UTC)', dataCollected='Собранные данные', dataReturned='Время передачи в kafka (UTC)')
    column_list = ('id', 'user_id', 'name', 'comment')
