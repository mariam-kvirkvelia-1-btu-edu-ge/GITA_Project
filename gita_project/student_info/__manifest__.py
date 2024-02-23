# -*- coding: utf-8 -*-
{
    'name': "GITA Project",
    'summary': """.""",
    'description': """.""",
    'author': "Mariam Kvirkvelia",
    'website': "",
    'module_type': 'official',
    'category': 'Services',
    # 'version': '17.0.1.0.0',

    'depends': ['base',
                'web',
                'mail',
                'crm'],

    # always loaded
    'data': [
        # 'data/sequences.xml',
        # 'security/groups.xml',
        # 'security/ir.model.access.csv',

        'views/management_system_views.xml',
        'report/report.xml',
        'report/report_card.xml',
    ],
    'license': 'LGPL-3',
    'bootstrap': True,
}
