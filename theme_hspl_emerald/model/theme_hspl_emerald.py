# -*- coding: utf-8 -*-
# © 2020 Heliconia Solutions Pvt. Ltd., < hello@heliconia.io >

from odoo import models

class theme_utils(models.AbstractModel):
    _inherit = 'theme.utils'
    
    
    def _theme_hspl_emerald_post_copy(self, mod):
        self.disable_view('website_theme_install.customize_modal')
