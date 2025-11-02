{
    'name': 'Legal Regulations Management',
    'version': '1.0.0',
    'category': 'Legal/Regulations',
    'summary': 'Manajemen peraturan hukum dan perundang-undangan',
    'description': """
        Legal Regulations Management
        ============================
        
        Modul untuk mengelola peraturan hukum dan perundang-undangan dengan fitur:
        - Tambah peraturan hukum
        - Kategori dokumen perundang-undangan
        - Informasi lengkap peraturan (nomor, bentuk, tahun, dll)
        - Status dan validitas peraturan
        - Pencarian dan filter peraturan
    """,
    'author': 'Legal Team',
    'license': 'LGPL-3',
    'depends': ['base', 'web', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/regulation_types.xml',
        'data/sample_regulations.xml',
        'data/additional_regulations.xml',
        'views/legal_regulation_views_minimal.xml',
        'views/menu_views.xml',
        'views/system_control_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}