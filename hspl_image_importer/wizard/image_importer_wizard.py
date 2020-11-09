# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import xlrd
import tempfile
import binascii
import base64
import io
import csv
import requests
import re
import os


class ImageImporterWizard(models.TransientModel):
    _name = 'image.importer.wizard'
    _description = 'Import image from csv or xls wizard'

    def get_model_domain(self):
        field_ids = self.env['ir.model.fields'].search([('ttype', '=', 'binary')])
        model_ids = field_ids.mapped('model_id').sorted('name').filtered(
            lambda m: not m.model.startswith('ir.') and not m.transient)
        return [('id', 'in', model_ids.ids)]

    model_id = fields.Many2one('ir.model', string='Model', domain=get_model_domain)
    binary_field_id = fields.Many2one('ir.model.fields', string='Image Field')
    file_input = fields.Binary(string='File', help='select csv or xls file')
    import_filename = fields.Char('File Name')
    error_msg = fields.Html('Error')
    state = fields.Selection([('init', 'init'), ('error', 'Error'), ('done', 'done')],
                             string='Status', readonly=True, default='init')

    @api.onchange('import_filename')
    def onchange_import_filename(self):
        if self.import_filename:
            import_type = self.import_filename.split('.')[-1]
            if import_type not in ['xlsx', 'xls', 'csv']:
                self.file_input = False
                raise UserError(_('Upload excel or csv file only.'))

    def is_valid_url(self, url):
        regex = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url is not None and regex.search(url)

    def check_image_is_available(self, file_url):
        results = requests.get(file_url, stream=True)
        if results.status_code != 200:
            return False
        return True

    def check_file_path_url(self, image_paths):
        error_path = []
        for path in image_paths:
            if self.is_valid_url(path):
                if not self.check_image_is_available(path):
                    error_path.append(path)
            else:
                if not os.path.isfile(path):
                    error_path.append(path)
        return error_path

    def get_record_id(self, reference):
        return self.env.ref(reference, False)

    def check_external_id_exists(self, external_ids):
        error_ids = []
        for reference in external_ids:
            record_id = self.get_record_id(reference)
            if not record_id:
                error_ids.append(reference)
            if record_id:
                if record_id._name != self.model_id.model:
                    error_ids.append(reference)
        return error_ids

    def check_xlsx_file(self):
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xls")
            fp.write(binascii.a2b_base64(self.file_input))
            fp.seek(0)
            workbook = xlrd.open_workbook(fp.name)
            workbook.sheet_by_index(0)
        except:
            raise UserError(_("Please Upload valid Excel File."))

    def check_csv_file(self):
        try:
            file = base64.b64decode(self.file_input)
            data = io.StringIO(file.decode("utf-8"))
            data.seek(0)
            file_reader = []
            csv_reader = csv.reader(data, delimiter=',')
            file_reader.extend(csv_reader)
        except:
            raise UserError(_("Please Upload valid CSV File."))

    def download_image_from_url(self, file_url):
        results = requests.get(file_url, stream=True)
        file_path = '/tmp/%s' % (file_url.split('/')[-1],)
        with open(file_path, 'wb') as f:
            f.write(results.content)
        return file_path

    def get_binary_data_from_path(self, file_path):
        encodedFile = False
        if os.path.isfile(file_path):
            with open(file_path, "rb") as f:
                encodedFile = base64.b64encode(f.read())
        else:
            raise UserError(_("%s Wrong path or File not Exists." % (file_path,)))
        return encodedFile

    def import_xlsx_file(self):
        self.check_xlsx_file()
        fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xls")
        fp.write(binascii.a2b_base64(self.file_input))
        fp.seek(0)
        workbook = xlrd.open_workbook(fp.name)
        sheet = workbook.sheet_by_index(0)
        keys = sheet.row_values(0)
        values = [sheet.row_values(i) for i in range(1, sheet.nrows)]
        external_ids = [v[0] for v in values]
        external_id_errors = self.check_external_id_exists(external_ids)
        image_paths = [v[1] for v in values]
        image_path_error = self.check_file_path_url(image_paths)
        if not external_id_errors and not image_path_error:
            for data in values:
                if self.is_valid_url(data[1]):
                    file_path = self.download_image_from_url(data[1])
                else:
                    file_path = data[1]
                if file_path and self.binary_field_id:
                    binary_data = self.get_binary_data_from_path(file_path)
                    record_id = self.get_record_id(data[0])
                    if record_id:
                        record_id.write({self.binary_field_id.name: binary_data})
            self.state = 'done'
        else:
            self.state = 'error'
            error_msg = '<div class="alert alert-warning" role="alert">'
            if external_id_errors:
                error_msg += '<div><b>Warning!</b> List of errors in External Ids:<div> \n\n'
                for error in external_id_errors:
                    err = error if error else 'No External Id'
                    error_msg += '<div> %s in Line no %d . </div>' % (err, external_ids.index(error) + 2)
            if image_path_error:
                error_msg += '<div><b>Warning!</b>List of errors in Path or Urls:</div> \n\n'
                for error in image_path_error:
                    err = error if error else 'No File path or URL'
                    error_msg += '<div> %s in Line no %d . </div>' % (err, image_paths.index(error) + 2)
            error_msg += '</div>'
            self.error_msg = error_msg

    def import_csv_file(self):
        self.check_csv_file()
        file = base64.b64decode(self.file_input)
        data = io.StringIO(file.decode("utf-8"))
        data.seek(0)
        file_reader = []
        csv_reader = csv.reader(data, delimiter=',')
        file_reader.extend(csv_reader)
        keys = file_reader[0]
        if len(keys) < 2:
            raise UserError(_('Please check your file headers.'))
        values = file_reader
        values.pop(0)
        external_ids = [v[0] for v in values]
        external_id_errors = self.check_external_id_exists(external_ids)
        image_paths = [v[1] for v in values]
        image_path_error = self.check_file_path_url(image_paths)
        if not external_id_errors and not image_path_error:
            for data in values:
                if self.is_valid_url(data[1]):
                    file_path = self.download_image_from_url(data[1])
                else:
                    file_path = data[1]
                if file_path and self.binary_field_id:
                    binary_data = self.get_binary_data_from_path(file_path)
                    record_id = self.get_record_id(data[0])
                    if record_id and binary_data:
                        record_id.write({self.binary_field_id.name: binary_data})
            self.state = 'done'
        else:
            self.state = 'error'
            error_msg = '<div class="alert alert-warning" role="alert">'
            if external_id_errors:
                error_msg += '<div><b>Warning!</b> List of error in External Ids:<div> \n\n'
                for error in external_id_errors:
                    err = error if error else 'No External Id'
                    error_msg += '<div> %s in Line no %d . </div>' % (err, external_ids.index(error) + 2)
            if image_path_error:
                error_msg += '<div><b>Warning!</b> Errors in Path or Urls.</div> \n\n'
                for error in image_path_error:
                    err = error if error else 'No File path or URL'
                    error_msg += '<div> %s in Line no %d . </div>' % (err, image_paths.index(error) + 2)
            error_msg += '</div>'
            self.error_msg = error_msg

    def import_data(self):
        if not self.import_filename:
            raise UserError(_('Upload excel or csv file only.'))
        import_type = self.import_filename.split('.')[-1]
        if import_type in ['xlsx', 'xls']:
            self.import_xlsx_file()
            name = 'Success' if self.state == 'done' else 'Error'
            return {
                'name': name,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'image.importer.wizard',
                'target': 'new',
                'res_id': self.id,
            }
        elif import_type in ['csv']:
            self.import_csv_file()
            name = 'Success' if self.state == 'done' else 'Error'
            return {
                'name': name,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_model': 'image.importer.wizard',
                'target': 'new',
                'res_id': self.id,
            }
        else:
            return {'type': 'ir.actions.act_window_close'}

    def action_reload(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
