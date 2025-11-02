# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class LegalRegulation(models.Model):
    _name = 'legal.regulation'
    _description = 'Legal Regulation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'hierarchy_order, tahun desc, nomor'
    _rec_name = 'judul'
    
    # Informasi Dasar - Diurutkan berdasarkan hierarki hukum Indonesia
    tipe_dokumen = fields.Selection([
        ('uud_1945', 'Undang-undang Dasar 1945'),
        ('tap_mpr', 'Ketetapan MPR'),
        ('undang_undang', 'Undang-Undang'),
        ('perpu', 'Peraturan Pemerintah Pengganti Undang-Undang'),
        ('peraturan_pemerintah', 'Peraturan Pemerintah'),
        ('peraturan_presiden', 'Peraturan Presiden'),
        ('keputusan_presiden', 'Keputusan Presiden'),
        ('instruksi_presiden', 'Instruksi Presiden'),
        ('peraturan_menteri', 'Peraturan Menteri'),
        ('keputusan_menteri', 'Keputusan Menteri'),
        ('peraturan_daerah', 'Peraturan Daerah'),
        ('peraturan_gubernur', 'Peraturan Gubernur'),
    ], string='Tipe Dokumen', required=True, default='undang_undang')
    
    # Field untuk menentukan urutan hierarki
    hierarchy_order = fields.Integer('Hierarchy Order', compute='_compute_hierarchy_order', store=True)
    
    judul = fields.Text('Judul', required=True, help='Judul lengkap peraturan')
    
    teu = fields.Char('T.E.U. (Tempat Terbit/Entitas Unit)', 
                      help='Contoh: Indonesia, Kementerian Pemberdayaan Perempuan dan Perlindungan Anak',
                      default='Indonesia')
    
    nomor = fields.Char('Nomor', required=True, help='Nomor peraturan')
    
    # Bentuk Peraturan
    bentuk = fields.Char('Bentuk', required=True, 
                         help='Contoh: Peraturan Menteri Pemberdayaan Perempuan Dan Perlindungan Anak')
    
    bentuk_singkat = fields.Char('Bentuk Singkat', 
                                 help='Contoh: Permen PPPA')
    
    # Tanggal dan Waktu
    tahun = fields.Integer('Tahun', required=True, default=lambda self: date.today().year)
    
    tempat_penetapan = fields.Char('Tempat Penetapan', default='Jakarta')
    
    tanggal_penetapan = fields.Date('Tanggal Penetapan', required=True)
    
    tanggal_pengundangan = fields.Date('Tanggal Pengundangan')
    
    tanggal_berlaku = fields.Date('Tanggal Berlaku')
    
    # Informasi Sumber dan Status
    sumber = fields.Text('Sumber', 
                         help='Contoh: BN 2025 (314); 70 hlm')
    
    subjek = fields.Text('Subjek', 
                         help='Contoh: KELUARGA, PERLINDUNGAN ANAK, PEREMPUAN / WANITA')
    
    status = fields.Selection([
        ('berlaku', 'Berlaku'),
        ('dicabut', 'Dicabut'),
        ('diubah', 'Diubah'),
        ('ditunda', 'Ditunda'),
        ('tidak_berlaku', 'Tidak Berlaku'),
    ], string='Status', required=True, default='berlaku')
    
    bahasa = fields.Selection([
        ('bahasa_indonesia', 'Bahasa Indonesia'),
        ('bahasa_inggris', 'Bahasa Inggris'),
        ('bahasa_daerah', 'Bahasa Daerah'),
    ], string='Bahasa', default='bahasa_indonesia')
    
    lokasi = fields.Char('Lokasi', 
                         help='Contoh: Kementerian Pemberdayaan Perempuan dan Perlindungan Anak')
    
    bidang = fields.Selection([
        ('hukum_pidana', 'HUKUM PIDANA'),
        ('hukum_perdata', 'HUKUM PERDATA'),
        ('hukum_administrasi_negara', 'HUKUM ADMINISTRASI NEGARA'),
        ('hukum_tata_negara', 'HUKUM TATA NEGARA'),
        ('hukum_internasional', 'HUKUM INTERNASIONAL'),
        ('hukum_bisnis', 'HUKUM BISNIS'),
        ('hukum_keluarga', 'HUKUM KELUARGA'),
        ('hukum_lingkungan', 'HUKUM LINGKUNGAN'),
        ('hukum_tenaga_kerja', 'HUKUM TENAGA KERJA'),
        ('hukum_pajak', 'HUKUM PAJAK'),
    ], string='Bidang Hukum')
    
    # Field Tambahan
    active = fields.Boolean('Active', default=True)
    
    keterangan = fields.Text('Keterangan Tambahan')
    
    # Field untuk Full-Text Search
    isi_peraturan = fields.Html('Isi Peraturan', help='Konten lengkap peraturan untuk pencarian mendalam')
    kata_kunci = fields.Text('Kata Kunci', help='Kata kunci tambahan untuk pencarian')
    ringkasan = fields.Text('Ringkasan', help='Ringkasan singkat peraturan')
    
    # Computed Fields
    nama_lengkap = fields.Char('Nama Lengkap', compute='_compute_nama_lengkap', store=True)
    
    is_berlaku_aktif = fields.Boolean('Berlaku Aktif', compute='_compute_is_berlaku_aktif')
    
    @api.depends('bentuk_singkat', 'nomor', 'tahun')
    def _compute_nama_lengkap(self):
        for record in self:
            if record.bentuk_singkat and record.nomor and record.tahun:
                record.nama_lengkap = f"{record.bentuk_singkat} No. {record.nomor} Tahun {record.tahun}"
            else:
                record.nama_lengkap = record.judul or 'Peraturan Baru'
    
    @api.depends('status', 'tanggal_berlaku')
    def _compute_is_berlaku_aktif(self):
        today = date.today()
        for record in self:
            if record.status == 'berlaku':
                if record.tanggal_berlaku:
                    record.is_berlaku_aktif = record.tanggal_berlaku <= today
                else:
                    record.is_berlaku_aktif = True
            else:
                record.is_berlaku_aktif = False
    
    @api.onchange('bentuk')
    def _onchange_bentuk(self):
        """Auto-generate bentuk_singkat dari bentuk"""
        if self.bentuk:
            # Mapping umum bentuk singkat
            bentuk_mapping = {
                'Undang-Undang': 'UU',
                'Peraturan Pemerintah': 'PP',
                'Peraturan Presiden': 'Perpres',
                'Peraturan Menteri': 'Permen',
                'Peraturan Daerah': 'Perda',
                'Keputusan Presiden': 'Keppres',
                'Keputusan Menteri': 'Kepmen',
                'Instruksi Presiden': 'Inpres',
                'Surat Edaran': 'SE',
            }
            
            for key, value in bentuk_mapping.items():
                if key.lower() in self.bentuk.lower():
                    self.bentuk_singkat = value
                    break
    
    @api.onchange('tanggal_penetapan')
    def _onchange_tanggal_penetapan(self):
        """Auto set tahun dari tanggal penetapan"""
        if self.tanggal_penetapan:
            self.tahun = self.tanggal_penetapan.year
            # Auto set tanggal berlaku jika belum diisi
            if not self.tanggal_berlaku:
                self.tanggal_berlaku = self.tanggal_penetapan
    
    # Computed Fields
    @api.depends('tipe_dokumen')
    def _compute_hierarchy_order(self):
        """Compute hierarchy order based on Indonesian legal hierarchy"""
        hierarchy_mapping = {
            'uud_1945': 1,           
            'tap_mpr': 2,            
            'undang_undang': 3,      
            'perpu': 4,              
            'peraturan_pemerintah': 5,  
            'peraturan_presiden': 6,    
            'keputusan_presiden': 7,    
            'instruksi_presiden': 8,    
            'peraturan_menteri': 9,     
            'keputusan_menteri': 10,    
            'peraturan_daerah': 11,     
            'peraturan_gubernur': 12,   
        }
        
        for record in self:
            record.hierarchy_order = hierarchy_mapping.get(record.tipe_dokumen, 999)

    @api.model
    def create(self, vals_list):
        """Override create untuk validasi"""
        # Handle both single dict and list of dicts
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
        
        for vals in vals_list:
            # Auto generate bentuk_singkat jika tidak ada
            if vals.get('bentuk') and not vals.get('bentuk_singkat'):
                bentuk = vals['bentuk']
                if 'Menteri' in bentuk:
                    vals['bentuk_singkat'] = 'Permen'
                elif 'Pemerintah' in bentuk:
                    vals['bentuk_singkat'] = 'PP'
                elif 'Presiden' in bentuk:
                    vals['bentuk_singkat'] = 'Perpres'
        
        return super(LegalRegulation, self).create(vals_list)
    
    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            if record.bentuk_singkat and record.nomor and record.tahun:
                name = f"{record.bentuk_singkat} No. {record.nomor}/{record.tahun}"
            else:
                name = record.judul[:50] + '...' if len(record.judul) > 50 else record.judul
            result.append((record.id, name))
        return result
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Enhanced search functionality"""
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', '|', '|', '|', '|', '|', '|',
                     ('judul', operator, name),
                     ('nomor', operator, name),
                     ('bentuk_singkat', operator, name),
                     ('subjek', operator, name),
                     ('keterangan', operator, name),
                     ('isi_peraturan', operator, name),
                     ('kata_kunci', operator, name),
                     ('ringkasan', operator, name),
                     ('bentuk', operator, name)]
        
        regulation_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(regulation_ids).name_get()


class LegalRegulationType(models.Model):
    _name = 'legal.regulation.type'
    _description = 'Legal Regulation Type'
    _order = 'sequence, name'
    
    name = fields.Char('Nama Tipe', required=True)
    code = fields.Char('Kode', required=True)
    description = fields.Text('Deskripsi')
    sequence = fields.Integer('Urutan', default=10)
    active = fields.Boolean('Active', default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Kode tipe peraturan harus unik!')
    ]