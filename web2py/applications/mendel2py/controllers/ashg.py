

@auth.requires_login()
@auth.requires_membership('lupskilab')
def index():
    ashg_form = SQLFORM.grid(db.ashg_data, editable=False, deletable=False, create=False)
    return dict(ashg_form = ashg_form)

