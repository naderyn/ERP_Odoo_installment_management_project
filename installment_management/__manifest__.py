{
    'name': 'Installment Management',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Manage customer installments and payments',
    'author': 'Nader',
    'depends': ['base', 'sale', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/installment_views.xml',
        
    ],
    'application': True,
    'install': True,
}
